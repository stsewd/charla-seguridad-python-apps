import os
import re
from django.utils.http import url_has_allowed_host_and_scheme
from urllib.parse import urlparse


def is_allowed_domain_in(url):
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    return "example.com" in hostname


def is_allowed_domain_regex(url):
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    pattern = re.compile(r"(.*.)?example.com")
    return pattern.match(domain)


def is_allowed_domain_regex2(url):
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    pattern = re.compile(r"(.*\.)?example.com$")
    return pattern.match(domain)


def is_allowed_domain_protocol_check(url):
    allowed_protocols = ["http", "https"]
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    has_valid_protocol = parsed.scheme in allowed_protocols
    valid_domain = "example.com"
    is_valid_domain = domain == valid_domain or domain.endswith(f".{valid_domain}")
    return has_valid_protocol and is_valid_domain


def is_allowed_domain_backslashes(url):
    allowed_protocols = ["http", "https"]
    url = url.replace("\\", "/")
    parsed = urlparse(url)
    domain = parsed.hostname or ""
    has_valid_protocol = parsed.scheme in allowed_protocols
    valid_domain = "example.com"
    is_valid_domain = domain == valid_domain or domain.endswith(f".{valid_domain}")
    return has_valid_protocol and is_valid_domain


def is_allowed_path_startswith(url):
    if not url_has_allowed_host_and_scheme(url, allowed_hosts=["example.com"]):
        return False
    parsed = urlparse(url)
    return parsed.path.startswith("/static/")


def is_allowed_path_normalize_path(url):
    allowed = "https://example.com/static/"
    if not url.startswith(allowed):
        return False
    parsed = urlparse(url)
    norm_path = os.path.normpath(parsed.path.replace("\\", "/"))
    if parsed.path.endswith("/"):
        norm_path += "/"
    if parsed.path != norm_path:
        return False
    return norm_path.startswith("/static/")
