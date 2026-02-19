# Simple in-memory cache to replace vectorstore-based implementation.
# This cache will reset when the process restarts; for persistent caching a
# database table could be used instead.

_cache_store: dict[str, str] = {}


def get_cached_answer(question: str) -> str | None:
    """Return previously stored answer or None if not found."""
    return _cache_store.get(question)


def save_to_cache(question: str, answer: str) -> None:
    """Store question-answer in the in-memory cache."""
    _cache_store[question] = answer
