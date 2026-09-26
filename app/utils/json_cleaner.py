import json
import re


def clean_and_parse_json(text: str) -> dict:
    """Robustly cleans and parses JSON responses from LLMs, handling markdown blocks,
    unescaped control characters, trailing commas, and partial truncation."""
    if not text or not text.strip():
        raise ValueError("LLM returned an empty response")

    # Strip code block wrappers
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    text = text.strip()

    # Direct parse attempt
    try:
        return json.loads(text, strict=False)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")

    if start == -1:
        raise ValueError("LLM response did not contain a JSON object.")

    if end == -1 or end <= start:
        json_str = text[start:] + "}"
    else:
        json_str = text[start:end + 1]

    try:
        return json.loads(json_str, strict=False)
    except Exception:
        pass

    # Trailing commas cleanup
    json_str = re.sub(r",\s*([}\]])", r"\1", json_str)
    try:
        return json.loads(json_str, strict=False)
    except Exception:
        pass

    # Unterminated string & bracket balance repair
    if json_str.count('"') % 2 != 0:
        json_str += '"'
    if json_str.count("[") > json_str.count("]"):
        json_str += "]"
    if json_str.count("{") > json_str.count("}"):
        json_str += "}"

    try:
        return json.loads(json_str, strict=False)
    except Exception as exc:
        raise ValueError(
            f"Could not parse JSON from LLM response: {exc}\nRAW RESPONSE:\n{text}"
        )
