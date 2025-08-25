"""Network utilities: ping, download, is_online, public_ip, random_user_agent."""
import random
import socket
import urllib.request

def ping(url, timeout=2):
    """Ping a URL (returns True if reachable)."""
    try:
        urllib.request.urlopen(url, timeout=timeout)
        return True
    except Exception:
        return False

def download(url, path):
    """Download a file from a URL to a local path."""
    urllib.request.urlretrieve(url, path)
    return path

def is_online():
    """Return True if the internet is reachable."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=2)
        return True
    except Exception:
        return False

def public_ip():
    """Return the public IP address (best effort)."""
    try:
        with urllib.request.urlopen('https://api.ipify.org') as f:
            return f.read().decode('utf-8')
    except Exception:
        return None

def random_user_agent():
    """Return a random user agent string."""
    agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        "Mozilla/5.0 (X11; Linux x86_64)",
        "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
        "Mozilla/5.0 (Android 11; Mobile; rv:89.0)",
        "curl/7.68.0",
        "Wget/1.20.3 (linux-gnu)",
        "python-requests/2.25.1"
    ]
    return random.choice(agents)
