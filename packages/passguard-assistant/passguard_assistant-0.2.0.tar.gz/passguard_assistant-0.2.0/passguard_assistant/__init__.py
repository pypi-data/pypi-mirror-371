from .core import PassGuard
from .checker import check_strength, estimate_entropy_bits
from .generator import suggest_password
from .alerts import SMTPConfig

__all__ = [
    "PassGuard",
    "check_strength",
    "estimate_entropy_bits",
    "suggest_password",
    "SMTPConfig",
]

__version__ = "0.2.0"
