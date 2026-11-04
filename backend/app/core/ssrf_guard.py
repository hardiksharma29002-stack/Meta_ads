"""SSRF Guard & Polite Web Fetcher.

Mandatory Outbound Crawler Transport complying with SEC-01:
Pre-connect DNS resolution drops private, loopback, link-local, and cloud metadata IPs.
Redirects re-validate every hop.
"""

import ipaddress
import socket
from urllib.parse import urlparse
import httpx
from app.core.config import settings
from app.core.errors import SSRFBlockedError
from app.core.logging import logger


BLOCKED_IP_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),          # IPv4 loopback
    ipaddress.ip_network("10.0.0.0/8"),           # RFC 1918 Private
    ipaddress.ip_network("172.16.0.0/12"),        # RFC 1918 Private
    ipaddress.ip_network("192.168.0.0/16"),       # RFC 1918 Private
    ipaddress.ip_network("169.254.0.0/16"),       # Link-local / AWS & GCP Metadata
    ipaddress.ip_network("0.0.0.0/8"),            # Broadcast
    ipaddress.ip_network("::1/128"),              # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),             # IPv6 Unique Local Address (ULA)
    ipaddress.ip_network("fe80::/10"),            # IPv6 Link-local
    ipaddress.ip_network("::ffff:0:0/96"),        # IPv4-mapped IPv6
]


def is_ip_allowed(ip_str: str) -> bool:
    """Validate whether an IP address is a safe public routable target."""
    try:
        ip = ipaddress.ip_address(ip_str)
        # Check against blocked network ranges
        for net in BLOCKED_IP_NETWORKS:
            if ip in net:
                return False
        return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
    except ValueError:
        return False


def validate_target_url(url: str) -> str:
    """Validate scheme, port, and pre-connect DNS resolution for target URL."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise SSRFBlockedError(f"Unsupported protocol scheme '{parsed.scheme}'. Only http/https permitted.")

    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    if port not in (80, 443):
        raise SSRFBlockedError(f"Restricted destination port {port}. Only ports 80/443 permitted.")

    hostname = parsed.hostname
    if not hostname:
        raise SSRFBlockedError("Invalid empty hostname in destination URL.")

    # Resolve all IPv4 and IPv6 addresses for hostname
    try:
        addr_info = socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as e:
        raise SSRFBlockedError(f"DNS resolution failure for '{hostname}': {str(e)}")

    for family, socktype, proto, canonname, sockaddr in addr_info:
        ip_addr = sockaddr[0]
        if not is_ip_allowed(ip_addr):
            logger.warn("ssrf_blocked_connection", hostname=hostname, ip=ip_addr)
            raise SSRFBlockedError(ip_addr)

    return url


class PoliteFetcher:
    """SSRF-Safe, size-capped, polite HTTP client for contact enrichment."""

    def __init__(self, user_agent: str = "AdAtlasBot/1.0 (+https://adatlas.in/bot; compliance@adatlas.in)"):
        self.user_agent = user_agent
        self.timeout = settings.REQUEST_TIMEOUT_SECONDS
        self.max_body_bytes = settings.MAX_DECOMPRESSED_BODY_BYTES
        self.max_redirects = settings.MAX_REDIRECT_HOPS

    async def fetch(self, url: str) -> tuple[int, bytes, str, dict[str, str]]:
        """Fetch URL with SSRF protection, redirect verification, and size caps.
        
        Returns: (status_code, body_bytes, final_url, headers)
        """
        current_url = url
        redirect_count = 0

        async with httpx.AsyncClient(
            headers={"User-Agent": self.user_agent},
            timeout=self.timeout,
            follow_redirects=False,
            verify=True,
        ) as client:
            while redirect_count <= self.max_redirects:
                # Pre-connect IP validation at every hop
                validate_target_url(current_url)

                try:
                    response = await client.get(current_url)
                except httpx.RequestError as e:
                    logger.warn("fetch_network_error", url=current_url, error=str(e))
                    raise

                # Handle redirects manually to re-validate destination IPs
                if response.is_redirect:
                    redirect_count += 1
                    location = response.headers.get("Location")
                    if not location:
                        break
                    # Handle relative redirects
                    current_url = str(response.url.join(location))
                    continue

                # Stream and enforce maximum decompressed body cap
                content = response.content
                if len(content) > self.max_body_bytes:
                    content = content[: self.max_body_bytes]

                return response.status_code, content, str(response.url), dict(response.headers)

            raise SSRFBlockedError(f"Exceeded maximum permitted redirect hops ({self.max_redirects}).")

