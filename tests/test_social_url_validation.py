import pytest
from unittest.mock import patch, MagicMock
import httpx
from app.utils.url_validator import (
    validate_social_url,
    normalize_url,
    URLValidationResult,
    check_reachability
)


def test_scenario_1_personal_linkedin_profile():
    url = "https://www.linkedin.com/in/johndoe"
    res = validate_social_url(url, designer_name="John Doe")
    assert res.verification_status == "VERIFIED"
    assert res.is_valid_format is True
    assert res.is_profile_type is True
    assert res.normalized_url == "https://www.linkedin.com/in/johndoe"


def test_scenario_2_regional_linkedin_profile():
    url = "https://in.linkedin.com/in/johndoe"
    res = validate_social_url(url, designer_name="John Doe")
    assert res.verification_status == "VERIFIED"
    assert res.is_valid_format is True
    assert res.is_profile_type is True
    assert res.normalized_url == "https://in.linkedin.com/in/johndoe"


def test_scenario_3_linkedin_company_page():
    url = "https://www.linkedin.com/company/studio-name"
    res = validate_social_url(url, designer_name="John Doe", studio_name="Studio Name")
    assert res.verification_status == "INVALID"
    assert res.is_profile_type is False
    assert "non-personal profile page type" in (res.rejection_reason or "")


def test_scenario_4_linkedin_legal_help_page():
    url = "https://www.linkedin.com/legal/user-agreement"
    res = validate_social_url(url, designer_name="John Doe")
    assert res.verification_status == "INVALID"
    assert res.is_profile_type is False


def test_scenario_5_linkedin_search_result_url():
    url = "https://www.linkedin.com/pub/dir/john/doe"
    res = validate_social_url(url, designer_name="John Doe")
    assert res.verification_status == "INVALID"
    assert res.is_profile_type is False


def test_scenario_6_instagram_profile():
    url = "https://www.instagram.com/johndoe_design/"
    res = validate_social_url(url, designer_name="John Doe", studio_name="John Doe Design")
    assert res.verification_status == "VERIFIED"
    assert res.is_valid_format is True
    assert res.is_profile_type is True
    assert res.normalized_url == "https://www.instagram.com/johndoe_design"


def test_scenario_7_instagram_reel_post_url():
    reel_url = "https://www.instagram.com/reel/C12345/"
    post_url = "https://www.instagram.com/p/C12345/"
    
    res_reel = validate_social_url(reel_url, designer_name="John Doe")
    assert res_reel.verification_status == "INVALID"
    assert res_reel.is_profile_type is False
    
    res_post = validate_social_url(post_url, designer_name="John Doe")
    assert res_post.verification_status == "INVALID"
    assert res_post.is_profile_type is False


def test_scenario_8_instagram_explore_directory_url():
    explore_url = "https://www.instagram.com/explore/tags/interiordesign/"
    dir_url = "https://www.instagram.com/directory/profiles/"
    
    res_exp = validate_social_url(explore_url, designer_name="John Doe")
    assert res_exp.verification_status == "INVALID"
    assert res_exp.is_profile_type is False

    res_dir = validate_social_url(dir_url, designer_name="John Doe")
    assert res_dir.verification_status == "INVALID"
    assert res_dir.is_profile_type is False


def test_scenario_9_url_with_tracking_parameters():
    url = "https://www.linkedin.com/in/johndoe?utm_source=share&utm_medium=member_desktop&igsh=123"
    norm = normalize_url(url)
    assert norm == "https://www.linkedin.com/in/johndoe"
    
    res = validate_social_url(url, designer_name="John Doe")
    assert res.normalized_url == "https://www.linkedin.com/in/johndoe"
    assert res.verification_status == "VERIFIED"


def test_scenario_10_non_existent_profile_404():
    url = "https://www.linkedin.com/in/thisuserdefinitelydoesnotexist99999"
    with patch("app.utils.url_validator.check_reachability") as mock_reach:
        mock_reach.return_value = (False, 404, "Page not found (HTTP 404)")
        res = validate_social_url(url, designer_name="This User", check_live=True)
        assert res.verification_status == "INVALID"
        assert res.is_reachable is False
        assert res.confidence == 0.0


def test_scenario_11_unreachable_profile_timeout():
    url = "https://www.linkedin.com/in/johndoe"
    with patch("app.utils.url_validator.check_reachability") as mock_reach:
        mock_reach.return_value = (False, 0, "Network connection error/timeout")
        res = validate_social_url(url, designer_name="John Doe", check_live=True)
        assert res.verification_status == "UNVERIFIED"
        assert res.is_reachable is False


def test_scenario_12_bot_protection_response_999_403():
    url = "https://www.linkedin.com/in/johndoe"
    with patch("app.utils.url_validator.check_reachability") as mock_reach:
        mock_reach.return_value = (False, 999, "Platform bot protection / authwall triggered (HTTP 999)")
        res = validate_social_url(url, designer_name="John Doe", check_live=True)
        assert res.verification_status == "BLOCKED_OR_UNVERIFIED"
        assert res.is_reachable is False


def test_scenario_13_identity_mismatch():
    url = "https://www.linkedin.com/in/completelyunrelatedperson"
    res = validate_social_url(
        url,
        designer_name="Ashiesh Shah",
        studio_name="Ashiesh Shah Atelier"
    )
    assert res.verification_status == "IDENTITY_MISMATCH"
    assert res.confidence == 0.0
    assert "does not match" in (res.rejection_reason or "")
