"""Unit & Security Tests for SSRF Guard (SEC-01).

Verifies that private, loopback, link-local, and cloud metadata IPs are rejected.
"""

import pytest
from app.core.ssrf_guard import is_ip_allowed, validate_target_url
from app.core.errors import SSRFBlockedError


def test_public_ips_allowed():
    """Verify that standard public Internet IPs are accepted."""
    assert is_ip_allowed("8.8.8.8") is True
    assert is_ip_allowed("1.1.1.1") is True
    assert is_ip_allowed("142.250.190.46") is True  # google.com IP


def test_private_and_loopback_ips_blocked():
    """Verify that loopback, RFC 1918, and metadata IPs are rejected (SEC-01)."""
    # IPv4 Loopback
    assert is_ip_allowed("127.0.0.1") is False
    assert is_ip_allowed("127.0.1.1") is False

    # Cloud Metadata (AWS, GCP, Azure, DigitalOcean)
    assert is_ip_allowed("169.254.169.254") is False
    assert is_ip_allowed("169.254.1.1") is False

    # RFC 1918 Private Ranges
    assert is_ip_allowed("10.0.0.1") is False
    assert is_ip_allowed("172.16.0.1") is False
    assert is_ip_allowed("192.168.1.1") is False

    # IPv6 Loopback & ULA
    assert is_ip_allowed("::1") is False
    assert is_ip_allowed("fc00::1") is False
    assert is_ip_allowed("fe80::1") is False
    assert is_ip_allowed("::ffff:127.0.0.1") is False


def test_validate_target_url_scheme_and_ports():
    """Verify that non-HTTP protocols and non-standard ports are rejected."""
    with pytest.raises(SSRFBlockedError):
        validate_target_url("file:///etc/passwd")

    with pytest.raises(SSRFBlockedError):
        validate_target_url("gopher://127.0.0.1:70")

    with pytest.raises(SSRFBlockedError):
        validate_target_url("http://example.com:22")  # SSH port blocked

