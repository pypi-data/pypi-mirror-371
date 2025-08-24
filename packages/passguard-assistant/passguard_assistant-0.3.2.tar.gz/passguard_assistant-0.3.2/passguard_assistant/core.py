# passguard_assistant/core.py
import hashlib
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

from .generator import suggest_password

# Optional imports for advanced features; fallback for testing
try:
    from .checker import check_strength as real_check_strength
except ImportError:
    real_check_strength = None

try:
    from .alerts import SMTPConfig, AttemptLogger, send_alert
except ImportError:
    SMTPConfig = None
    AttemptLogger = None
    send_alert = None

RATING_ORDER = ["Very Weak", "Weak", "Fair", "Good", "Strong"]


@dataclass
class PassGuardConfig:
    admin_email: Optional[str] = None
    smtp: Optional[Any] = None
    failed_threshold: int = 3
    failed_window_sec: int = 600
    state_path: Optional[str] = None


class PassGuard:
    def __init__(
        self,
        admin_email: Optional[str] = None,
        smtp: Optional[Any] = None,
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

        # Logger setup, fallback if AttemptLogger missing
        if AttemptLogger:
            self._logger = AttemptLogger(
                admin_email=admin_email or "",
                smtp=smtp,
                threshold=failed_threshold,
                window_sec=failed_window_sec,
                state_path=state_path,
            )
        else:
            self._logger = None

    # ---------- Health ----------
    def check_strength(self, password: str, name: Optional[str] = None) -> Dict[str, Any]:
        """Analyze the strength of a given password and return detailed info."""
        if real_check_strength:
            result = real_check_strength(password, name=name)
        else:
            # fallback dummy checker
            score = 0
            if len(password) >= 8:
                score += 1
            if any(c.isupper() for c in password):
                score += 1
            if any(c.islower() for c in password):
                score += 1
            if any(c.isdigit() for c in password):
                score += 1
            if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?/" for c in password):
                score += 1
            weak_name = name.lower() in password.lower() if name else False
            rating = "Strong" if score >= 4 else "Good" if score == 3 else "Fair" if score == 2 else "Weak"
            result = {"score": score, "weak_name_included": weak_name, "rating": rating}

        # Suggest password if weak
        if result.get("rating") in ("Very Weak", "Weak"):
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
        ok = RATING_ORDER.index(info.get("rating", "Weak")) >= RATING_ORDER.index(minimum)
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
        if self._logger:
            return self._logger.log(success=success, ip=ip, user_agent=user_agent, username=username)
        # fallback dummy
        return {"success": success, "ip": ip, "user_agent": user_agent, "username": username}

    def notify(self, subject: str, message: str) -> None:
        """Send an alert email to the configured admin."""
        if SMTPConfig and send_alert and self.config.admin_email:
            smtp = self.config.smtp or SMTPConfig.from_env()
            send_alert(smtp, self.config.admin_email, subject, message)

    # ---------- Integrations ----------
    def report_suspicious(self, details: str) -> None:
        """Call this from your app if you detect suspicious access."""
        self.notify("[PassGuard] Suspicious activity reported", details)
