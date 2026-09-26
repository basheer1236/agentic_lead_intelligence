from rapidfuzz import fuzz

from app.tools.ad_directory_tool import (
    fetch_ad_directory,
    find_directory_profile,
)
from app.tools.ad_search_tool import search_ad


class DesignerResolver:
    """
    Resolve an extracted designer/studio against Architectural Digest.

    Resolution order:

        1. AD PRO Directory
        2. AD Search -> AD PRO Directory profiles
        3. Return not_found

    Important:
        - Never assume two designers are the same.
        - Never use an unrelated article title as proof of identity.
        - Fuzzy similarity alone is NOT sufficient for resolution.
        - Exact/normalized identity matches can be resolved automatically.
        - Ambiguous cases are not automatically accepted.
    """

    DIRECTORY_PROFILE_PATH = "/adpro/directory/profile/"

    def resolve(
        self,
        designer_name: str | None = None,
        studio_name: str | None = None,
    ) -> dict:
        """
        Resolve an extracted designer or studio.

        Args:
            designer_name:
                Designer/person name extracted from the article.

            studio_name:
                Studio/company name extracted from the article.

        Returns:
            Dictionary containing resolution status,
            matched entity, source, URL and confidence.
        """

        # ---------------------------------------------------------
        # 1. Clean input
        # ---------------------------------------------------------

        designer_name = self._clean_name(designer_name)
        studio_name = self._clean_name(studio_name)

        if not designer_name and not studio_name:
            return self._unresolved(
                reason="No designer or studio name provided"
            )

        # ---------------------------------------------------------
        # 2. AD PRO DIRECTORY
        # ---------------------------------------------------------

        directory_result = self._search_ad_directory(
            designer_name=designer_name,
            studio_name=studio_name,
        )

        if directory_result:
            return directory_result

        # ---------------------------------------------------------
        # 3. AD SEARCH FALLBACK
        # ---------------------------------------------------------

        search_candidates = self._search_ad_search(
            designer_name=designer_name,
            studio_name=studio_name,
        )

        # ---------------------------------------------------------
        # 4. Only consider AD PRO DIRECTORY profiles
        #
        # Ordinary AD articles are NOT identity matches.
        # ---------------------------------------------------------

        directory_candidates = [
            candidate
            for candidate in search_candidates
            if self._is_directory_profile(candidate)
        ]

        if not directory_candidates:
            return self._not_found(
                candidate_count=len(search_candidates)
            )

        # ---------------------------------------------------------
        # 5. Deterministic identity matching
        # ---------------------------------------------------------

        match = self._find_exact_or_normalized_match(
            designer_name=designer_name,
            studio_name=studio_name,
            candidates=directory_candidates,
        )

        if match:
            return {
                "status": "resolved",
                "source": "ad_search",
                "matched_name": match["matched_name"],
                "profile_url": match["profile_url"],
                "matched_query": match["matched_query"],
                "confidence": match["confidence"],
                "match_type": match["match_type"],
                "candidate_count": len(directory_candidates),
            }

        # ---------------------------------------------------------
        # 6. Fuzzy candidates are deliberately NOT accepted
        #
        # Example:
        #
        # The Comma Collective
        #          ↓
        # Ekaa - The Design Collective
        #
        # Even if fuzzy similarity = 0.82,
        # this is NOT enough to establish identity.
        # ---------------------------------------------------------

        return self._not_found(
            candidate_count=len(directory_candidates)
        )

    # =============================================================
    # AD PRO DIRECTORY
    # =============================================================

    def _search_ad_directory(
        self,
        designer_name: str | None,
        studio_name: str | None,
    ) -> dict | None:
        """
        Search AD PRO Directory first.

        This is the preferred designer enrichment source.
        """

        try:
            directory_html = fetch_ad_directory()

            match = find_directory_profile(
                directory_html,
                designer_name=designer_name,
                studio_name=studio_name,
            )

        except Exception as exc:
            print(
                f"[DesignerResolver] AD Directory lookup failed: {exc}"
            )
            return None

        if not match:
            return None

        matched_name = match.get("matched_name")
        matched_query = match.get("matched_query")
        profile_url = match.get("profile_url")

        # ---------------------------------------------------------
        # Verify the directory result before accepting it.
        # ---------------------------------------------------------

        confidence, match_type = self._calculate_directory_confidence(
            designer_name=designer_name,
            studio_name=studio_name,
            matched_name=matched_name,
            matched_query=matched_query,
        )

        # Do NOT blindly trust the directory search.
        if confidence < 0.95:
            return None

        return {
            "status": "resolved",
            "source": "ad_pro_directory",
            "matched_name": matched_name,
            "profile_url": profile_url,
            "matched_query": matched_query,
            "confidence": confidence,
            "match_type": match_type,
            "candidate_count": 1,
        }

    # =============================================================
    # AD SEARCH
    # =============================================================

    def _search_ad_search(
        self,
        designer_name: str | None,
        studio_name: str | None,
    ) -> list[dict]:
        """
        Search AD Search using available identity information.
        """

        queries = []

        # Studio is usually the stronger organizational identity.
        if studio_name:
            queries.append(studio_name)

        if designer_name:
            queries.append(designer_name)

        candidates = []
        seen_urls = set()

        for query in queries:

            try:
                results = search_ad(query)

            except Exception as exc:
                print(
                    f"[DesignerResolver] AD Search failed "
                    f"for '{query}': {exc}"
                )
                continue

            for result in results:

                url = result.get("url")

                if not url:
                    continue

                if url in seen_urls:
                    continue

                seen_urls.add(url)

                candidates.append(
                    {
                        "title": result.get(
                            "title",
                            "",
                        ).strip(),
                        "url": url,
                        "query": query,
                    }
                )

        return candidates

    # =============================================================
    # EXACT / NORMALIZED MATCHING
    # =============================================================

    def _find_exact_or_normalized_match(
        self,
        designer_name: str | None,
        studio_name: str | None,
        candidates: list[dict],
    ) -> dict | None:
        """
        Find an exact or normalized identity match.

        Fuzzy similarity is intentionally NOT used for automatic
        resolution.

        Examples:

            "The Comma Collective"
            "the comma collective"

        -> RESOLVED

        But:

            "The Comma Collective"
            "Ekaa - The Design Collective"

        -> NOT FOUND
        """

        designer_normalized = (
            self._normalize(designer_name)
            if designer_name
            else None
        )

        studio_normalized = (
            self._normalize(studio_name)
            if studio_name
            else None
        )

        for candidate in candidates:

            candidate_title = candidate.get(
                "title",
                "",
            ).strip()

            candidate_normalized = self._normalize(
                candidate_title
            )

            if not candidate_normalized:
                continue

            # -----------------------------------------------------
            # Exact studio match
            # -----------------------------------------------------

            if (
                studio_normalized
                and candidate_normalized == studio_normalized
            ):
                return {
                    "matched_name": candidate_title,
                    "profile_url": candidate["url"],
                    "matched_query": candidate["query"],
                    "confidence": 1.0,
                    "match_type": "exact_studio_match",
                }

            # -----------------------------------------------------
            # Exact designer match
            # -----------------------------------------------------

            if (
                designer_normalized
                and candidate_normalized == designer_normalized
            ):
                return {
                    "matched_name": candidate_title,
                    "profile_url": candidate["url"],
                    "matched_query": candidate["query"],
                    "confidence": 1.0,
                    "match_type": "exact_designer_match",
                }

            # -----------------------------------------------------
            # Strong token equality
            #
            # This handles harmless formatting differences such as:
            #
            # "Studio ABC"
            # "Studio ABC Design"
            #
            # BUT only when the complete identity tokens strongly
            # correspond.
            # -----------------------------------------------------

            if studio_normalized:

                if self._tokens_match(
                    studio_normalized,
                    candidate_normalized,
                ):
                    return {
                        "matched_name": candidate_title,
                        "profile_url": candidate["url"],
                        "matched_query": candidate["query"],
                        "confidence": 0.98,
                        "match_type": "normalized_studio_match",
                    }

            if designer_normalized:

                if self._tokens_match(
                    designer_normalized,
                    candidate_normalized,
                ):
                    return {
                        "matched_name": candidate_title,
                        "profile_url": candidate["url"],
                        "matched_query": candidate["query"],
                        "confidence": 0.98,
                        "match_type": "normalized_designer_match",
                    }

        return None

    # =============================================================
    # DIRECTORY CONFIDENCE
    # =============================================================

    def _calculate_directory_confidence(
        self,
        designer_name: str | None,
        studio_name: str | None,
        matched_name: str | None,
        matched_query: str | None,
    ) -> tuple[float, str]:
        """
        Calculate confidence for an AD Directory match.

        IMPORTANT:
        Fuzzy similarity alone is not sufficient.

        Only exact/normalized matches return high confidence.
        """

        if not matched_name:
            return 0.0, "no_match"

        matched_normalized = self._normalize(
            matched_name
        )

        # ---------------------------------------------------------
        # Studio exact match
        # ---------------------------------------------------------

        if studio_name:

            studio_normalized = self._normalize(
                studio_name
            )

            if matched_normalized == studio_normalized:
                return 1.0, "exact_studio_match"

            if self._tokens_match(
                studio_normalized,
                matched_normalized,
            ):
                return 0.98, "normalized_studio_match"

        # ---------------------------------------------------------
        # Designer exact match
        # ---------------------------------------------------------

        if designer_name:

            designer_normalized = self._normalize(
                designer_name
            )

            if matched_normalized == designer_normalized:
                return 1.0, "exact_designer_match"

            if self._tokens_match(
                designer_normalized,
                matched_normalized,
            ):
                return 0.98, "normalized_designer_match"

        # ---------------------------------------------------------
        # Fuzzy similarity deliberately rejected
        # ---------------------------------------------------------

        return 0.0, "fuzzy_only_rejected"

    # =============================================================
    # TOKEN MATCH
    # =============================================================

    @staticmethod
    def _tokens_match(
        value1: str,
        value2: str,
    ) -> bool:
        """
        Determine whether two normalized names have essentially
        the same meaningful tokens.

        This is stricter than simple fuzzy similarity.
        """

        if not value1 or not value2:
            return False

        tokens1 = set(value1.split())
        tokens2 = set(value2.split())

        if not tokens1 or not tokens2:
            return False

        # Exact token equality.
        if tokens1 == tokens2:
            return True

        # One set must contain the other, but only when the shared
        # identity is substantial.
        smaller = min(
            tokens1,
            tokens2,
            key=len,
        )

        larger = max(
            tokens1,
            tokens2,
            key=len,
        )

        if smaller.issubset(larger):

            # Avoid matching generic one-word names such as:
            # "Design" -> "Design Studio"
            #
            # Require at least 2 meaningful tokens.
            if len(smaller) >= 2:
                return True

        return False

    # =============================================================
    # HELPERS
    # =============================================================

    @staticmethod
    def _clean_name(
        value: str | None,
    ) -> str | None:
        """
        Clean an extracted identity value without changing
        its meaning.
        """

        if value is None:
            return None

        value = value.strip()

        if not value:
            return None

        return value

    @staticmethod
    def _normalize(
        value: str,
    ) -> str:
        """
        Normalize names for deterministic comparison.

        Example:

            "The Comma Collective"
            "the comma collective"

        become:

            "the comma collective"
        """

        value = value.lower().strip()

        punctuation = [
            ",",
            ".",
            "-",
            "_",
            "/",
            "&",
            "(",
            ")",
            ":",
        ]

        for char in punctuation:
            value = value.replace(
                char,
                " ",
            )

        # Collapse multiple spaces.
        value = " ".join(
            value.split()
        )

        return value

    @classmethod
    def _is_directory_profile(
        cls,
        candidate: dict,
    ) -> bool:
        """
        Check whether an AD Search result is an actual
        AD PRO Directory profile.
        """

        url = candidate.get(
            "url",
            "",
        )

        return (
            cls.DIRECTORY_PROFILE_PATH
            in url
        )

    @staticmethod
    def _not_found(
        candidate_count: int = 0,
    ) -> dict:
        return {
            "status": "not_found",
            "source": None,
            "matched_name": None,
            "profile_url": None,
            "matched_query": None,
            "confidence": 0.0,
            "match_type": None,
            "candidate_count": candidate_count,
        }

    @staticmethod
    def _unresolved(
        reason: str,
    ) -> dict:
        return {
            "status": "unresolved",
            "source": None,
            "matched_name": None,
            "profile_url": None,
            "matched_query": None,
            "confidence": 0.0,
            "match_type": None,
            "candidate_count": 0,
            "reason": reason,
        }