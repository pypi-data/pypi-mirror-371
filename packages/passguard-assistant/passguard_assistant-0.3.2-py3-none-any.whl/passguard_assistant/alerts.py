
import os
import json
import time
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Optional, Dict, Any

@dataclass
class SMTPConfig:
    host: str
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    from_email: Optional[str] = None
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> "SMTPConfig":
        return cls(
            host=os.environ.get("PASSGUARD_SMTP_HOST", ""),
            port=int(os.environ.get("PASSGUARD_SMTP_PORT", "587")),
            username=os.environ.get("PASSGUARD_SMTP_USER"),
            password=os.environ.get("PASSGUARD_SMTP_PASS"),
            from_email=os.environ.get("PASSGUARD_FROM_EMAIL"),
            use_tls=True,
        )

def send_alert(smtp: SMTPConfig, to_email: str, subject: str, body: str) -> None:
    if not smtp.host or not to_email:
        return
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = smtp.from_email or smtp.username or "no-reply@example.com"
    msg["To"] = to_email
    msg.set_content(body)

    context = ssl.create_default_context()
    with smtplib.SMTP(smtp.host, smtp.port, timeout=15) as server:
        if smtp.use_tls:
            server.starttls(context=context)
        if smtp.username and smtp.password:
            server.login(smtp.username, smtp.password)
        server.send_message(msg)

class AttemptLogger:
    def __init__(self, admin_email: str, smtp: Optional[SMTPConfig] = None,
                 threshold: int = 3, window_sec: int = 600, state_path: Optional[str] = None):
        self.admin_email = admin_email
        self.smtp = smtp or SMTPConfig.from_env()
        self.threshold = threshold
        self.window_sec = window_sec
        self.state_path = state_path
        self._state = {"attempts": []}
        self._load()

    def _load(self):
        if self.state_path and os.path.exists(self.state_path):
            try:
                with open(self.state_path, "r", encoding="utf-8") as f:
                    self._state = json.load(f)
            except Exception:
                self._state = {"attempts": []}

    def _save(self):
        if self.state_path:
            try:
                with open(self.state_path, "w", encoding="utf-8") as f:
                    json.dump(self._state, f)
            except Exception:
                pass

    def log(self, success: bool, ip: Optional[str]=None, user_agent: Optional[str]=None,
            username: Optional[str]=None) -> Dict[str, Any]:
        now = time.time()
        self._state.setdefault("attempts", []).append({
            "ts": now, "success": bool(success), "ip": ip, "ua": user_agent, "username": username
        })

        cutoff = now - self.window_sec
        self._state["attempts"] = [a for a in self._state["attempts"] if a["ts"] >= cutoff]

        fails = sum(1 for a in self._state["attempts"] if not a["success"])
        triggered = False
        if fails >= self.threshold and self.admin_email:
            triggered = True
            subject = f"[PassGuard] {fails} failed login attempts detected"
            body = "Detected {} failed login attempts within the last {} seconds.\nRecent events:\n".format(fails, self.window_sec)
            body += "\\n".join(
                "- {ts} | user={username} ip={ip} ua={ua} success={success}".format(**{
                    "ts": __import__("time").strftime("%Y-%m-%d %H:%M:%S", __import__("time").localtime(a["ts"])),
                    "username": a.get("username"),
                    "ip": a.get("ip"),
                    "ua": a.get("ua"),
                    "success": a["success"],
                }) for a in self._state["attempts"][-10:]
            )
            try:
                send_alert(self.smtp, self.admin_email, subject, body)
            except Exception:
                pass

        self._save()
        return {"fails_in_window": fails, "threshold": self.threshold, "alert_triggered": triggered, "window_sec": self.window_sec}
