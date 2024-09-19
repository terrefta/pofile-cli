import os

from ..client.pofile import (
    get_api_domain_url,
    get_api_url_for_download_endpoint,
    get_api_url_for_upload_endpoint,
)


def test_get_api_domain_url(monkeypatch):
    # Default domain
    assert get_api_domain_url() == "https://pofile.io"
    # Custom domain
    monkeypatch.setenv("POFILE_API_DOMAIN_URL", "https://test.pofile.io")
    assert os.getenv("POFILE_API_DOMAIN_URL") == "https://test.pofile.io"
    assert get_api_domain_url() == "https://test.pofile.io"


def test_get_api_url_for_download_endpoint(monkeypatch):
    # Default
    assert (
        get_api_url_for_download_endpoint("446b3553-7f62-4ec2-b3fc-b18708e3ff6a")
        == "https://pofile.io/api/download/446b3553-7f62-4ec2-b3fc-b18708e3ff6a/"
    )
    # Custom domain
    monkeypatch.setenv("POFILE_API_DOMAIN_URL", "https://test.pofile.io")
    assert os.getenv("POFILE_API_DOMAIN_URL") == "https://test.pofile.io"
    assert (
        get_api_url_for_download_endpoint("446b3553-7f62-4ec2-b3fc-b18708e3ff6a")
        == "https://test.pofile.io/api/download/446b3553-7f62-4ec2-b3fc-b18708e3ff6a/"
    )


def test_get_api_url_for_upload_endpoint(monkeypatch):
    # Default
    assert get_api_url_for_upload_endpoint() == "https://pofile.io/api/upload/"
    # Custom domain
    monkeypatch.setenv("POFILE_API_DOMAIN_URL", "https://test.pofile.io")
    assert os.getenv("POFILE_API_DOMAIN_URL") == "https://test.pofile.io"
    assert get_api_url_for_upload_endpoint() == "https://test.pofile.io/api/upload/"
