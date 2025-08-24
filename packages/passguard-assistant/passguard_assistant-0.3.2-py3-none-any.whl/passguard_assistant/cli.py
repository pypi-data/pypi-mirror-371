# passguard_assistant/cli.py
import argparse
import json
import sys
import time

from .core import PassGuard
from . import hasher
from .generator import token_urlsafe, token_hex

def animate_logo():
    """Display a short honey badger animation before showing CLI."""
    frames = [
        r"""
   (\_._/) 
   ( o o )  Honey Badger!
   /  V  \ 
        """,
        r"""
   (\_._/) 
   ( o o )  Analyzing...
   /  V  \ 
        """,
        r"""
   (\_._/) 
   ( o o )  Ready to guard!
   /  V  \ 
        """
    ]
    for frame in frames:
        sys.stdout.write("\033c")  # Clear screen
        print(frame)
        time.sleep(0.5)
    print("\n")  # Spacer before CLI

def main():
    animate_logo()  # Show animation first

    parser = argparse.ArgumentParser(
        prog="passguard",
        description="PassGuard Assistant - Password health, hashing, and security toolkit"
    )
    sub = parser.add_subparsers(dest="cmd")

    # --- check ---
    p_check = sub.add_parser(
        "check",
        help="Analyze password strength"
    )
    p_check.add_argument("password", help="Password to analyze")
    p_check.add_argument(
        "--name",
        default=None,
        help="Optional personal name for weak password detection"
    )

    # --- suggest ---
    p_suggest = sub.add_parser(
        "suggest",
        help="Suggest a strong password"
    )
    p_suggest.add_argument("--length", type=int, default=16, help="Length of password")
    p_suggest.add_argument(
        "--no-ensure-all",
        dest="no_ensure_all",
        action="store_true",
        help="Do not force inclusion of all character classes",
    )

    # --- log ---
    p_log = sub.add_parser("log", help="Log a login attempt")
    group = p_log.add_mutually_exclusive_group(required=True)
    group.add_argument("--success", action="store_true", help="Mark attempt as successful")
    group.add_argument("--failed", action="store_true", help="Mark attempt as failed")
    p_log.add_argument("--ip", default=None, help="IP address of attempt")
    p_log.add_argument("--username", default=None, help="Username of attempt")
    p_log.add_argument("--user-agent", default=None, help="Browser/Client info")

    # --- hash ---
    p_hash = sub.add_parser(
        "hash",
        help="Hash a password using Argon2, bcrypt, or PBKDF2"
    )
    p_hash.add_argument("password", help="Password to hash")
    p_hash.add_argument("--algo", choices=["argon2", "bcrypt", "pbkdf2"], default="argon2")
    p_hash.add_argument("--bcrypt-rounds", type=int, default=hasher.BCRYPT_ROUNDS_DEFAULT)
    p_hash.add_argument("--pbkdf2-iterations", type=int, default=hasher.PBKDF2_DEFAULT["iterations"])

    # --- verify ---
    p_verify = sub.add_parser(
        "verify",
        help="Verify a password against a stored hash"
    )
    p_verify.add_argument("password", help="Password to verify")
    p_verify.add_argument("hash", help="Stored hash to verify against")

    # --- token ---
    p_tok = sub.add_parser("token", help="Generate a secure token")
    p_tok.add_argument("--format", choices=["urlsafe", "hex"], default="urlsafe")
    p_tok.add_argument("--bytes", type=int, default=32, help="Strength in bytes (before encoding)")

    args = parser.parse_args()
    pg = PassGuard()

    # --- handle commands ---
    if args.cmd == "check":
        out = pg.check_strength(args.password, name=getattr(args, "name", None))
        print(json.dumps(out, indent=2))

    elif args.cmd == "suggest":
        print(pg.suggest_password(length=args.length, ensure_all_classes=not args.no_ensure_all))

    elif args.cmd == "log":
        out = pg.log_attempt(
            success=args.success,
            ip=args.ip,
            user_agent=args.user_agent,
            username=args.username,
        )
        print(json.dumps(out, indent=2))

    elif args.cmd == "hash":
        policy = hasher.HashPolicy(
            algo=args.algo,
            bcrypt_rounds=args.bcrypt_rounds,
            pbkdf2_iterations=getattr(args, "pbkdf2_iterations", hasher.PBKDF2_DEFAULT["iterations"]),
        )
        print(hasher.hash_password(args.password, algo=args.algo, policy=policy))

    elif args.cmd == "verify":
        ok = hasher.verify_password(args.password, args.hash)
        print("OK" if ok else "NO")
        sys.exit(0 if ok else 1)

    elif args.cmd == "token":
        print(token_urlsafe(args.bytes) if args.format == "urlsafe" else token_hex(args.bytes))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
