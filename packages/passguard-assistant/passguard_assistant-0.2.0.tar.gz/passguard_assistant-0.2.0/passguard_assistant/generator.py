
import secrets
import string

AMBIGUOUS = set("Il1O0")

def _random_from(charset: str, length: int) -> str:
    return "".join(secrets.choice(charset) for _ in range(length))

def suggest_password(length: int = 16, ensure_all_classes: bool = True, avoid_ambiguous: bool = True) -> str:
    lowers = set(string.ascii_lowercase)
    uppers = set(string.ascii_uppercase)
    digits = set(string.digits)
    symbols = set("!@#$%^&*()-_=+[]{};:,.?/\\|`~")

    if avoid_ambiguous:
        for s in (lowers, uppers, digits):
            s.difference_update(AMBIGUOUS)

    pool = "".join(sorted(lowers | uppers | digits | symbols))

    if length < 8:
        length = 8

    if not ensure_all_classes:
        return _random_from(pool, length)

    req = [
        secrets.choice("".join(sorted(lowers))),
        secrets.choice("".join(sorted(uppers))),
        secrets.choice("".join(sorted(digits))),
        secrets.choice("".join(sorted(symbols))),
    ]
    remaining = length - len(req)
    rest = _random_from(pool, remaining)
    all_chars = list("".join(req) + rest)
    for i in range(len(all_chars)-1, 0, -1):
        j = secrets.randbelow(i+1)
        all_chars[i], all_chars[j] = all_chars[j], all_chars[i]
    return "".join(all_chars)
