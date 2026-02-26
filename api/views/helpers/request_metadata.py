import hashlib
from typing import Any

from rest_framework.request import Request
from user_agents import parse as parse_user_agent

from api.models import LoginEvent, User


def get_client_ip(request: Request) -> str:
    """Get client IP address, handling proxies and load balancers"""
    # Check for forwarded IP (from load balancer/proxy)
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first
        return str(x_forwarded_for).split(",")[0].strip()
    if request.META.get("HTTP_X_REAL_IP"):
        return str(request.META.get("HTTP_X_REAL_IP"))
    return str(request.META.get("REMOTE_ADDR", "unknown"))


def parse_user_agent_string(user_agent_string: str) -> dict[str, str | None]:
    """Parse user agent string into components"""
    if not user_agent_string:
        return {
            "user_agent": "",
            "device_type": None,
            "browser": None,
            "browser_version": None,
            "os": None,
            "os_version": None,
        }

    try:
        ua = parse_user_agent(user_agent_string)

        return {
            "user_agent": user_agent_string,
            "device_type": _get_device_type(ua),
            "browser": ua.browser.family if ua.browser else None,
            "browser_version": ".".join(map(str, ua.browser.version[:2]))
            if ua.browser and ua.browser.version
            else None,
            "os": ua.os.family if ua.os else None,
            "os_version": ".".join(map(str, ua.os.version[:2]))
            if ua.os and ua.os.version
            else None,
        }
    except (AttributeError, ValueError, IndexError):
        # Fallback if parsing fails
        pass

    # Fallback: basic parsing without user-agents library
    return {
        "user_agent": user_agent_string,
        "device_type": _detect_device_type_basic(user_agent_string),
        "browser": _detect_browser_basic(user_agent_string),
        "browser_version": None,
        "os": _detect_os_basic(user_agent_string),
        "os_version": None,
    }


def _get_device_type(ua: Any) -> str:
    """Determine device type from user agent"""
    if ua.is_mobile:
        return "mobile"
    if ua.is_tablet:
        return "tablet"
    return "desktop"


def _detect_device_type_basic(user_agent: str) -> str | None:
    """Basic device type detection without user-agents library"""
    user_agent_lower = user_agent.lower()
    if (
        "mobile" in user_agent_lower
        or "android" in user_agent_lower
        or "iphone" in user_agent_lower
    ):
        return "mobile"
    if "tablet" in user_agent_lower or "ipad" in user_agent_lower:
        return "tablet"
    return "desktop"


def _detect_browser_basic(user_agent: str) -> str | None:
    """Basic browser detection without user-agents library"""
    user_agent_lower = user_agent.lower()
    if "chrome" in user_agent_lower and "edg" not in user_agent_lower:
        return "Chrome"
    if "firefox" in user_agent_lower:
        return "Firefox"
    if "safari" in user_agent_lower and "chrome" not in user_agent_lower:
        return "Safari"
    if "edg" in user_agent_lower:
        return "Edge"
    if "opera" in user_agent_lower:
        return "Opera"
    return None


def _detect_os_basic(user_agent: str) -> str | None:
    """Basic OS detection without user-agents library"""
    user_agent_lower = user_agent.lower()
    if "windows" in user_agent_lower:
        return "Windows"
    if "mac" in user_agent_lower or "darwin" in user_agent_lower:
        return "macOS"
    if "linux" in user_agent_lower:
        return "Linux"
    if "android" in user_agent_lower:
        return "Android"
    if "ios" in user_agent_lower or "iphone" in user_agent_lower or "ipad" in user_agent_lower:
        return "iOS"
    return None


def generate_device_fingerprint(
    user_agent: str, ip: str, additional_data: dict[str, Any] | None = None
) -> str:
    """
    Generate a device fingerprint hash.

    This creates a hash based on device characteristics to help identify
    the same device across sessions (for security purposes).
    """
    fingerprint_data = f"{user_agent}|{ip}"

    if additional_data:
        # Add screen resolution, timezone, language, etc. if available
        fingerprint_data += f"|{additional_data.get('screen_resolution', '')}"
        fingerprint_data += f"|{additional_data.get('timezone', '')}"
        fingerprint_data += f"|{additional_data.get('language', '')}"

    # Create SHA-256 hash
    return hashlib.sha256(fingerprint_data.encode("utf-8")).hexdigest()


def get_login_metadata(
    request: Request, login_method: str = "password", failure_reason: str | None = None
) -> dict[str, Any]:
    """
    Extract all login metadata from request.

    Args:
      request: Django request object
      login_method: Method used for login (password, google, facebook)
      success: Whether login was successful
      failure_reason: Reason for failure if login failed

    Returns:
      Dictionary containing all login metadata
    """
    ip_address = get_client_ip(request)
    user_agent_string = request.META.get("HTTP_USER_AGENT", "")
    ua_data = parse_user_agent_string(user_agent_string)

    # Generate device fingerprint
    additional_metadata = {
        "screen_resolution": request.META.get("HTTP_X_SCREEN_RESOLUTION"),
        "timezone": request.META.get("HTTP_X_TIMEZONE"),
        "language": request.META.get("HTTP_ACCEPT_LANGUAGE", "").split(",")[0]
        if request.META.get("HTTP_ACCEPT_LANGUAGE")
        else None,
    }
    device_fingerprint = generate_device_fingerprint(
        user_agent_string, ip_address, additional_metadata
    )

    return {
        "ip_address": ip_address,
        "user_agent": ua_data["user_agent"],
        "device_type": ua_data["device_type"],
        "browser": ua_data["browser"],
        "browser_version": ua_data["browser_version"],
        "os": ua_data["os"],
        "os_version": ua_data["os_version"],
        "login_method": login_method,
        "success": failure_reason is None,
        "failure_reason": failure_reason,
        "device_fingerprint": device_fingerprint,
        "metadata": {
            k: v for k, v in additional_metadata.items() if v
        },  # Only include non-None values
    }


def create_failed_login_event(
    user: User, request: Request, login_method: str = "password", failure_reason: str | None = None
) -> None:
    """
    Create a failed login event for a user.
    """
    metadata = get_login_metadata(request, login_method=login_method, failure_reason=failure_reason)
    LoginEvent.objects.create(user=user, **metadata)
