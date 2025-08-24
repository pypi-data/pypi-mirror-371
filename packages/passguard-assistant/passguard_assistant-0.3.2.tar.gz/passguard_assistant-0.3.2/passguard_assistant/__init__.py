# passguard_assistant/__init__.py
from .core import PassGuard
from .checker import check_strength, estimate_entropy_bits
from .generator import suggest_password, token_urlsafe, token_hex
from .alerts import SMTPConfig
from . import hasher

__all__ = [
    "PassGuard",
    "check_strength",
    "estimate_entropy_bits",
    "suggest_password",
    "token_urlsafe",
    "token_hex",
    "SMTPConfig",
    "hasher",
]

__version__ = "0.3.2"
