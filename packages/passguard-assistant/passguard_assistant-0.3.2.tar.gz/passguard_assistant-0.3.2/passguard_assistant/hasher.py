from __future__ import annotations
from typing import Optional
import base64
import hashlib
import hmac
import re
import secrets

import bcrypt
from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

# --- Defaults ---
BCRYPT_ROUNDS_DEFAULT = 12
PBKDF2_DEFAULT = {"iterations": 100_000}

# --- Argon2 instance ---
argon2_hasher = Argon2Hasher(time_cost=2, memory_cost=102400, parallelism=8)

# --- Base64 helpers for PBKDF2 ---
_B64 = lambda b: base64.urlsafe_b64encode(b).decode("ascii").rstrip("=")
_UNB64 = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4))
_PBKDF2_TAG = "pbkdf2_sha256"

# --- Regex for algorithm detection ---
_ARGON2_RE = re.compile(r"^\$argon2(?:id|i|d)\$.*")  
_BCRYPT_RE = re.compile(r"^\$2[aby]\$")


# --- HashPolicy class for CLI usage ---
class HashPolicy:
    def __init__(
        self,
        algo="argon2",
        bcrypt_rounds=BCRYPT_ROUNDS_DEFAULT,
        pbkdf2_iterations=PBKDF2_DEFAULT["iterations"]
    ):
        self.algo = algo
        self.bcrypt_rounds = bcrypt_rounds
        self.pbkdf2_iterations = pbkdf2_iterations


# --- Infer algorithm from stored hash ---
def get_algorithm(hashed: str) -> str:
    if _ARGON2_RE.match(hashed):
        return "argon2"
    if _BCRYPT_RE.match(hashed):
        return "bcrypt"
    if hashed.startswith(_PBKDF2_TAG + "$"):
        return "pbkdf2"
    raise ValueError("Unrecognized hash format")


# --- Hashing function ---
def hash_password(password: str, algo: str = "argon2", policy: Optional[HashPolicy] = None) -> str:
    if not isinstance(password, str):
        raise TypeError("password must be a string")
    policy = policy or HashPolicy(algo=algo.lower())

    if policy.algo == "argon2":
        return argon2_hasher.hash(password)

    elif policy.algo == "bcrypt":
        rounds = max(4, int(policy.bcrypt_rounds))
        salt = bcrypt.gensalt(rounds)
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    elif policy.algo == "pbkdf2":
        salt = secrets.token_bytes(16)
        dk = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            max(100_000, int(policy.pbkdf2_iterations)),
            dklen=32
        )
        return f"{_PBKDF2_TAG}${policy.pbkdf2_iterations}${_B64(salt)}${_B64(dk)}"

    else:
        raise ValueError("Unsupported algo. Use 'argon2', 'bcrypt', or 'pbkdf2'.")


# --- Verification function ---
def verify_password(password: str, hashed: str, policy: Optional[HashPolicy] = None) -> bool:
    algo = get_algorithm(hashed)
    policy = policy or HashPolicy(algo=algo)

    if algo == "argon2":
        try:
            return argon2_hasher.verify(hashed, password)
        except VerifyMismatchError:
            return False

    elif algo == "bcrypt":
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

    elif algo == "pbkdf2":
        try:
            _, iter_s, salt_s, dk_s = hashed.split("$", 3)
            iterations = int(iter_s)
            salt = _UNB64(salt_s)
            dk_expected = _UNB64(dk_s)
            dk = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                iterations,
                dklen=len(dk_expected)
            )
            return hmac.compare_digest(dk, dk_expected)
        except Exception:
            return False

    return False


# --- Check if a hash needs rehash ---
def needs_rehash(hashed: str, policy: Optional[HashPolicy] = None) -> bool:
    algo = get_algorithm(hashed)
    policy = policy or HashPolicy(algo=algo)

    if algo == "argon2":
        try:
            return argon2_hasher.check_needs_rehash(hashed)
        except Exception:
            return False

    if algo == "bcrypt":
        m = re.search(r"\$2[aby]\$(\d{2})\$", hashed)
        if not m:
            return True
        return int(m.group(1)) < policy.bcrypt_rounds

    if algo == "pbkdf2":
        try:
            _, iter_s, *_ = hashed.split("$", 3)
            return int(iter_s) < policy.pbkdf2_iterations
        except Exception:
            return True

    return False
