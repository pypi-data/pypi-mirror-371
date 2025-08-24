# PassGuard Assistant 🔐

<p align="center">
  <img src="https://raw.githubusercontent.com/your-username/passguard-assistant/main/logo.png" width="180" alt="PassGuard Logo">
</p>

A privacy-friendly **Password Health + Security Assistant** library.

---

## Features
- ✅ Password strength checker with **entropy score (0–100)**
- ✅ Detects **personal info** (name, DOB, phone numbers)
- ✅ Strong password generator (with symbols, uppercase, lowercase, digits)
- ✅ If weak → auto-suggests **secure random password + SHA256 hash**
- ✅ Rotation reminders (1, 3, 6 months)
- ✅ Failed-attempt logging with optional email alerts
- ✅ Simple CLI support (`passguard check`, `passguard suggest`, `passguard log`)

---

## Security & Privacy
- 🚫 **No OS-level monitoring** (no keyloggers, no clipboard access).  
- ✅ Works only **inside your app/backend** with provided hooks.  
- 🔒 Logs (failed attempts, reminders) are fully under your control.  
- 📧 Email alerts are **optional** and use your SMTP credentials.  

---

## Installation
```bash
pip install passguard-assistant
