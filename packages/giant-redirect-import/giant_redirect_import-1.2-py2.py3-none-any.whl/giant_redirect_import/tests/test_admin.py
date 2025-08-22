import pytest

from ..admin import ensure_trailing_slash, check_leading_slash, extract_path, check_full_url


def test_ensure_trailing_slash_adds_slash():
    assert ensure_trailing_slash("/apple") == "/apple/"


def test_ensure_trailing_slash_not_added():
    assert ensure_trailing_slash("/apple/") == "/apple/"


def test_check_leading_slash_adds_slash():
    assert check_leading_slash("apple/") == "/apple/"


def test_check_leading_slash_does_not_add_slash():
    assert check_leading_slash("/apple") == "/apple"


def test_extract_path_isolates_path():
    assert extract_path("http://www.client-domain.org.uk/on-site") == "/on-site/"


def test_extract_path_returns_original_path():
    assert extract_path("/on-site/") == "/on-site/"


def test_check_full_url_adds_scheme():
    assert check_full_url("google.com") == "https://google.com/"


def test_check_full_url_adds_slashes():
    assert check_full_url("page_3") == "/page_3/"