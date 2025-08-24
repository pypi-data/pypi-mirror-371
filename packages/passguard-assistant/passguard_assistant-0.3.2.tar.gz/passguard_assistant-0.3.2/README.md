# PassGuard Assistant 🔐

<p align="center">
  <img src="https://raw.githubusercontent.com/sathishkevinmitnick/passguard-assistant/main/logo.png" width="180" alt="PassGuard Logo">
</p>

A privacy-friendly **Password Health + Security Assistant** library with an **interactive CLI** for terminal users.

---

## Features
- ✅ Password strength checker with **entropy score (0–100)**
- ✅ Detects **personal info** (name, DOB, phone numbers)
- ✅ Strong password generator (symbols, uppercase, lowercase, digits)
- ✅ If weak → auto-suggests **secure random password + SHA256 hash**
- ✅ Rotation reminders (1, 3, 6 months)
- ✅ Failed-attempt logging with optional email alerts
- ✅ Secure password hashing (`argon2`, `bcrypt`, `pbkdf2`)
- ✅ Password verification
- ✅ Secure token generation (`urlsafe` and `hex`)
- ✅ **Interactive CLI with terminal UI** (ready to guard!)

---

## Security & Privacy
- 🚫 **No OS-level monitoring** (no keyloggers, no clipboard access)
- ✅ Works only **inside your app/backend** with provided hooks
- 🔒 Logs (failed attempts, reminders) are fully under your control
- 📧 Email alerts are **optional** and use your SMTP credentials

---

## CLI Usage Example

```bash
passguard
