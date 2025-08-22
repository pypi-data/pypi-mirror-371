from __future__ import annotations
import argparse, sys
from .browser import create_driver
from .waits import SmartWait, By

def main(argv=None):
    parser = argparse.ArgumentParser(prog="advsel", description="Advanced Selenium CLI")
    parser.add_argument("url", nargs="?", help="URL to open for a quick smoke-check")
    parser.add_argument("--browser", default="chrome", choices=["chrome", "firefox"], help="Browser to use")
    parser.add_argument("--headless", action="store_true", help="Run headless")
    parser.add_argument("--timeout", type=int, default=20, help="Wait timeout")
    args = parser.parse_args(argv)

    if not args.url:
        parser.print_help()
        return 0

    drv = create_driver(browser=args.browser, headless=args.headless)
    try:
        drv.get(args.url)
        SmartWait(drv, timeout=args.timeout).visible((By.TAG_NAME, "body"))
        title = drv.title or "(no title)"
        print(f"[advsel] Loaded: {args.url} — Title: {title}")
        return 0
    finally:
        drv.quit()

if __name__ == "__main__":
    raise SystemExit(main())