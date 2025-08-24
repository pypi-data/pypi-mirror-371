import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .checker import check_strength
from .generator import suggest_password
from .alerts import SMTPConfig, AttemptLogger, send_alert

RATING_ORDER = ["Very Weak", "Weak", "Fair", "Good", "Strong"]


@dataclass
class PassGuardConfig:
    admin_email: Optional[str] = None
    smtp: Optional[SMTPConfig] = None
    failed_threshold: int = 3
    failed_window_sec: int = 600
    state_path: Optional[str] = None  # where to keep attempt logs


class PassGuard:
    def __init__(
        self,
        admin_email: Optional[str] = None,
        smtp: Optional[SMTPConfig] = None,
        failed_threshold: int = 3,
        failed_window_sec: int = 600,
        state_path: Optional[str] = None
    ):
        self.config = PassGuardConfig(
            admin_email=admin_email,
            smtp=smtp,
            failed_threshold=failed_threshold,
            failed_window_sec=failed_window_sec,
            state_path=state_path,
        )
        self._logger = AttemptLogger(
            admin_email=admin_email or "",
            smtp=smtp,
            threshold=failed_threshold,
            window_sec=failed_window_sec,
            state_path=state_path,
        )

    # ---------- Health ----------
    def check_strength(self, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze the strength of a given password and return detailed info."""
        result = check_strength(password, name=name)

        if result["rating"] in ("Very Weak", "Weak"):
            suggestion = suggest_password(length=16, ensure_all_classes=True)
            encrypted = hashlib.sha256(suggestion.encode()).hexdigest()
            result["suggested_password"] = suggestion
            result["encrypted_suggestion"] = encrypted

        return result

    def suggest_password(
        self,
        length: int = 16,
        ensure_all_classes: bool = True,
        avoid_ambiguous: bool = True
    ) -> str:
        """Generate a strong password suggestion."""
        return suggest_password(
            length=length,
            ensure_all_classes=ensure_all_classes,
            avoid_ambiguous=avoid_ambiguous,
        )

    def compare(self, password: str, minimum: str = "Strong") -> Dict[str, Any]:
        """Return whether the password meets a minimum rating."""
        info = self.check_strength(password)
        ok = RATING_ORDER.index(info["rating"]) >= RATING_ORDER.index(minimum)
        return {
            "meets_minimum": ok,
            "minimum": minimum,
            "analysis": info,
        }

    # ---------- Rotation/Memory ----------
    def reset_reminder(self, months: int, remember_flag: int = 1) -> Dict[str, Any]:
        """Calculate when a user should reset their password."""
        if months not in (1, 3, 6):
            months = 3
        now = datetime.utcnow()
        next_reset = now + timedelta(days=30 * months)
        action = "normal"

        if remember_flag == 0:
            next_reset = now + timedelta(days=7)
            action = "early_reset_suggested"

        return {
            "now_utc": now.isoformat() + "Z",
            "next_reset_utc": next_reset.isoformat() + "Z",
            "policy_months": months,
            "remember_flag": remember_flag,
            "action": action,
        }

    # ---------- Attempts & Alerts ----------
    def log_attempt(
        self,
        success: bool,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        username: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log login attempts and trigger alerts if threshold exceeded."""
        return self._logger.log(success=success, ip=ip, user_agent=user_agent, username=username)

    def notify(self, subject: str, message: str) -> None:
        """Send an alert email to the configured admin."""
        smtp = self.config.smtp or SMTPConfig.from_env()
        if self.config.admin_email:
            send_alert(smtp, self.config.admin_email, subject, message)

    # ---------- Integrations ----------
    def report_suspicious(self, details: str) -> None:
        """Call this from your app if you detect suspicious access to credentials, etc."""
        self.notify("[PassGuard] Suspicious activity reported", details)
