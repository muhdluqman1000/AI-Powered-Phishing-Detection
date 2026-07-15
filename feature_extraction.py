import re
from urllib.parse import urlparse


def normalize_url(url):
    url = str(url).strip()

    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    parsed = urlparse(url)

    # Remove trailing slash only for root homepage URLs
    if parsed.path == "/" and not parsed.query:
        url = url.rstrip("/")

    return url


def extract_features(url):
    url = normalize_url(url)

    features = {}

    parsed = urlparse(url)
    hostname = parsed.netloc
    path = parsed.path

    features["url_length"] = len(url)
    features["hostname_length"] = len(hostname)
    features["path_length"] = len(path)

    features["num_dots"] = url.count(".")
    features["num_hyphens"] = url.count("-")
    features["num_slashes"] = url.count("/")
    features["num_digits"] = sum(c.isdigit() for c in url)
    features["num_special_chars"] = sum(not c.isalnum() for c in url)

    features["has_at"] = 1 if "@" in url else 0
    features["has_https"] = 1 if url.startswith("https") else 0
    features["has_ip"] = 1 if re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", url) else 0
    features["has_query"] = 1 if "?" in url else 0
    features["has_equal"] = 1 if "=" in url else 0

    suspicious_words = [
        "login",
        "verify",
        "secure",
        "account",
        "update",
        "bank",
        "signin"
    ]

    features["has_suspicious_word"] = 1 if any(
        word in url.lower() for word in suspicious_words
    ) else 0

    return features