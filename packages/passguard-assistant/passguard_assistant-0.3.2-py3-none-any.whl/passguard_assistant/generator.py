# passguard_assistant/generator.py
import secrets
import string
from typing import Iterable, Optional

# --- Ambiguous characters that are often confused ---
AMBIGUOUS = set("O0Il1|`'\";:,./\\")
# Default full alphabet
DEFAULT_ALPHABET = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation


def _random_from(charset: str, length: int) -> str:
    """Return a cryptographically-random string from the given charset."""
    return "".join(secrets.choice(charset) for _ in range(length))


def _secure_shuffle(items: list) -> None:
    """Fisher–Yates shuffle using secrets for cryptographic randomness (in-place)."""
    for i in range(len(items) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        items[i], items[j] = items[j], items[i]


def suggest_password(
    length: int = 16,
    ensure_all_classes: bool = True,
    avoid_ambiguous: bool = True,
    min_classes: int = 3,
    use_symbols: bool = True,
    extra_symbols: Optional[str] = None,
    exclude_chars: Optional[Iterable[str]] = None,
) -> str:
    """
    Generate a strong cryptographically secure password.

    Args:
        length: desired length (minimum enforced to 8)
        ensure_all_classes: ensure at least `min_classes` of the 4 classes (lower/upper/digit/symbol)
        avoid_ambiguous: remove ambiguous characters (e.g., O/0, I/l/1)
        min_classes: minimum distinct classes required (1..4)
        use_symbols: include punctuation symbols
        extra_symbols: extra symbols to add
        exclude_chars: iterable of characters to exclude

    Returns:
        A strong password string
    """
    if length < 8:
        length = 8

    # Character classes
    lowers = set(string.ascii_lowercase)
    uppers = set(string.ascii_uppercase)
    digits = set(string.digits)
    symbols = set(string.punctuation) if use_symbols else set()
    if extra_symbols:
        symbols.update(extra_symbols)

    # Remove ambiguous characters if requested
    if avoid_ambiguous:
        lowers -= AMBIGUOUS
        uppers -= AMBIGUOUS
        digits -= AMBIGUOUS
        symbols -= AMBIGUOUS

    # Remove explicitly excluded characters
    if exclude_chars:
        excl = set(exclude_chars)
        lowers -= excl
        uppers -= excl
        digits -= excl
        symbols -= excl

    # Build pool
    pool_set = lowers | uppers | digits | symbols
    if not pool_set:
        pool_set = (set(string.ascii_letters) | set(string.digits)) - AMBIGUOUS
    pool = "".join(sorted(pool_set))

    if not ensure_all_classes:
        return _random_from(pool, length)

    # Ensure min_classes characters from different classes
    available_classes = [
        ("lower", "".join(sorted(lowers))),
        ("upper", "".join(sorted(uppers))),
        ("digit", "".join(sorted(digits))),
        ("symbol", "".join(sorted(symbols))),
    ]
    non_empty = [(name, chars) for name, chars in available_classes if chars]
    min_classes = max(1, min(min_classes, len(non_empty)))

    guaranteed = [secrets.choice(chars) for _, chars in non_empty[:min_classes]]
    remaining = max(0, length - len(guaranteed))
    remainder = _random_from(pool, remaining)
    all_chars = list("".join(guaranteed) + remainder)
    _secure_shuffle(all_chars)
    pw = "".join(all_chars)

    # Validate classes count (rare edge case)
    classes_hit = [
        any(c.islower() for c in pw),
        any(c.isupper() for c in pw),
        any(c.isdigit() for c in pw),
        any(c in string.punctuation for c in pw) if use_symbols else False,
    ]
    if sum(classes_hit) < min_classes:
        return suggest_password(
            length=length,
            ensure_all_classes=ensure_all_classes,
            avoid_ambiguous=avoid_ambiguous,
            min_classes=min_classes,
            use_symbols=use_symbols,
            extra_symbols=extra_symbols,
            exclude_chars=exclude_chars,
        )

    return pw


def token_urlsafe(nbytes: int = 32) -> str:
    """Generate a URL-safe cryptographic token."""
    return secrets.token_urlsafe(nbytes)


def token_hex(nbytes: int = 32) -> str:
    """Generate a hex token."""
    return secrets.token_hex(nbytes)
