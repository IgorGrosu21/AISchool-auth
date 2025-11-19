from contextvars import ContextVar
from typing import Iterable

from .settings import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES

_language_context: ContextVar[str] = ContextVar("language_context", default=DEFAULT_LANGUAGE)


def normalize_language(language: str, supported: Iterable[str] | None = None) -> str:
    """Normalize language code to supported languages."""
    if not language:
        return DEFAULT_LANGUAGE

    supported_set = set(supported or SUPPORTED_LANGUAGES)
    language = language.lower()

    if language in supported_set:
        return language

    # Accept forms like "en-US" -> "en"
    primary = language.split("-")[0]
    if primary in supported_set:
        return primary

    return DEFAULT_LANGUAGE


def set_language(language: str):
    """Set the current language context."""
    normalized = normalize_language(language)
    return _language_context.set(normalized)


def get_language() -> str:
    """Get the current language context."""
    return _language_context.get()


def reset_language(token) -> None:
    """Reset the language context to a previous value."""
    if token is not None:
        _language_context.reset(token)

