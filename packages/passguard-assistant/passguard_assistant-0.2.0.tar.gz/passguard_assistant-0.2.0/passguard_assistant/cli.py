import argparse
import json
from .core import PassGuard


def main():
    parser = argparse.ArgumentParser(
        prog="passguard",
        description="Password health + security assistant"
    )
    sub = parser.add_subparsers(dest="cmd")

    # --- check ---
    p_check = sub.add_parser("check", help="Analyze password strength")
    p_check.add_argument("password", help="Password to analyze")
    p_check.add_argument("--name", default=None, help="Optional personal name to detect")

    # --- suggest ---
    p_suggest = sub.add_parser("suggest", help="Suggest a strong password")
    p_suggest.add_argument("--length", type=int, default=16, help="Length of password")
    p_suggest.add_argument(
        "--no-ensure-all",
        dest="no_ensure_all",
        action="store_true",
        help="Do not force inclusion of all character classes"
    )

    # --- log ---
    p_log = sub.add_parser("log", help="Log a login attempt (and maybe alert)")
    group = p_log.add_mutually_exclusive_group(required=True)
    group.add_argument("--success", action="store_true", help="Mark attempt as successful")
    group.add_argument("--failed", action="store_true", help="Mark attempt as failed")
    p_log.add_argument("--ip", default=None, help="IP address of attempt")
    p_log.add_argument("--username", default=None, help="Username of attempt")
    p_log.add_argument("--user-agent", default=None, help="Browser/Client info")

    args = parser.parse_args()
    pg = PassGuard()

    # --- handle commands ---
    if args.cmd == "check":
        out = pg.check_strength(args.password, name=args.name)
        print(json.dumps(out, indent=2))

    elif args.cmd == "suggest":
        out = pg.suggest_password(
            length=args.length,
            ensure_all_classes=not args.no_ensure_all
        )
        print(out)

    elif args.cmd == "log":
        success = args.success
        out = pg.log_attempt(
            success=success,
            ip=args.ip,
            user_agent=args.user_agent,
            username=args.username,
        )
        print(json.dumps(out, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
