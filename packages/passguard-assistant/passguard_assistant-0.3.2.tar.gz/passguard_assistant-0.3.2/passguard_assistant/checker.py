import math
import re
import string
from typing import Optional

# Common dictionary passwords (short set; can expand with data/common_passwords.txt later)
COMMON_SMALL = {
    "123456", "password", "123456789", "qwerty", "abc123",
    "111111", "123123", "password1", "iloveyou", "admin",
    "letmein", "welcome", "monkey", "dragon", "qwerty123",
}


def _has_sequence(pw: str, min_len: int = 3) -> bool:
    """Detect ascending sequences like abc or 123"""
    if len(pw) < min_len:
        return False
    count = 1
    for i in range(1, len(pw)):
        if ord(pw[i]) == ord(pw[i-1]) + 1:
            count += 1
            if count >= min_len:
                return True
        else:
            count = 1
    return False


def _charspace_size(pw: str) -> int:
    """Estimate character set size based on classes present"""
    space = 0
    if any(c.islower() for c in pw): space += 26
    if any(c.isupper() for c in pw): space += 26
    if any(c.isdigit() for c in pw): space += 10
    if any(c in string.punctuation for c in pw): space += len(set(string.punctuation))
    if any(not (c.isdigit() or c.isalpha() or c in string.punctuation) for c in pw):
        space += 32
    return max(space, 1)


def _estimate_entropy_bits(password: str) -> float:
    """Shannon-style entropy estimation (with penalties)"""
    N = _charspace_size(password)
    L = len(password)
    penalty = 0
    if _has_sequence(password):
        penalty += min(L * 0.5, 10)
    if len(set(password)) <= max(1, L // 3):  # low uniqueness
        penalty += min(L * 0.6, 12)
    return max(0.0, L * math.log2(N) - penalty)


def _contains_personal_info(password: str, name: Optional[str] = None) -> list:
    """Detect personal info patterns inside password"""
    issues = []
    pw_lower = password.lower()

    # Check name
    if name and name.lower() in pw_lower:
        issues.append("Avoid including your name in the password.")

    # DOB patterns (yyyy, ddmmyyyy, etc.)
    if re.search(r"(19|20)\d{2}", password):  # year
        issues.append("Avoid using your birth year in passwords.")
    if re.search(r"\d{2}[/-]?\d{2}[/-]?\d{2,4}", password):
        issues.append("Avoid using date of birth or full dates.")

    # Phone-like numbers
    if re.search(r"\d{10}", password):
        issues.append("Avoid including phone numbers in the password.")

    return issues


def check_strength(password: str, name: Optional[str] = None) -> dict:
    """Full password health check with score, rating, and tips"""
    if not isinstance(password, str):
        raise TypeError("password must be a string")

    length = len(password)
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)

    # common or too short
    too_short_common = length <= 12
    in_common = password.lower() in COMMON_SMALL
    common_password = too_short_common or in_common

    sequential = _has_sequence(password)
    entropy = round(_estimate_entropy_bits(password), 2)

    # Check for personal info
    personal_issues = _contains_personal_info(password, name=name)

    # Scoring system (0–100)
    score = 0
    score += min(length * 2, 20)            # length up to 20 pts
    score += 10 if has_lower else 0
    score += 10 if has_upper else 0
    score += 10 if has_digit else 0
    score += 10 if has_symbol else 0
    score += min(int(entropy // 10), 30)    # entropy up to 30 pts
    if not common_password: score += 5
    if not sequential: score += 5
    if not personal_issues: score += 10

    score = min(score, 100)

    # Rating map
    if score < 30:
        rating = "Very Weak"
    elif score < 50:
        rating = "Weak"
    elif score < 70:
        rating = "Fair"
    elif score < 85:
        rating = "Good"
    else:
        rating = "Strong"

    # Actionable tips
    tips = []
    if length < 12:
        tips.append("Use at least 12–16 characters.")
    if sum([has_lower, has_upper, has_digit, has_symbol]) < 3:
        tips.append("Mix lower, upper, digits, and symbols.")
    if common_password:
        tips.append("Avoid common or short passwords.")
    if sequential:
        tips.append("Avoid sequential patterns like 'abc', '123'.")
    if entropy < 60:
        tips.append("Increase randomness; avoid repeated words or patterns.")
    tips.extend(personal_issues)

    return {
        "length": length,
        "classes": {
            "lower": has_lower, "upper": has_upper,
            "digit": has_digit, "symbol": has_symbol
        },
        "entropy_bits": entropy,
        "common_password": common_password,
        "sequential_pattern": sequential,
        "personal_info_detected": bool(personal_issues),
        "score": score,
        "rating": rating,
        "tips": tips,
    }


def estimate_entropy_bits(password: str) -> float:
    """Estimate entropy of a password in bits (simple raw calculation)."""
    charset = 0
    if any(c.islower() for c in password): charset += 26
    if any(c.isupper() for c in password): charset += 26
    if any(c.isdigit() for c in password): charset += 10
    if any(not c.isalnum() for c in password): charset += 32  # rough symbol count

    if charset == 0:
        return 0.0

    entropy = len(password) * math.log2(charset)
    return round(entropy, 2)
