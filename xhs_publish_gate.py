#!/usr/bin/env python3
"""Gate hourly Xiaohongshu auto-publish runs.

Behavior (Asia/Shanghai):
- 08:00-22:59: if today's content has unpublished items, publish with 1/10 probability.
- 23:00-23:59: if today's content has unpublished items, force publish.
- Otherwise: print nothing and exit 0, so callers can stop silently.

Default output is intentionally minimal:
- prints "PUBLISH" when the caller should continue normal publish workflow
- prints "FORCE_PUBLISH" at 23:00 when unpublished content still exists
- prints nothing when the caller should do nothing
"""
from __future__ import annotations

import argparse
import random
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TZ = ZoneInfo("Asia/Shanghai")
DEFAULT_ROOT = Path(__file__).resolve().parent
IMAGE_PATTERNS = ("*.jpg", "*.jpeg", "*.png", "*.webp")


def has_publishable_item(root: Path, day: str) -> bool:
    day_dir = root / day
    if not day_dir.is_dir():
        return False

    for item_dir in sorted(
        (p for p in day_dir.iterdir() if p.is_dir() and p.name.isdigit()),
        key=lambda p: int(p.name),
    ):
        if (item_dir / "published").exists():
            continue
        if not (item_dir / "post_content.md").is_file():
            continue
        if not (item_dir / "publish_log.md").is_file():
            continue
        if any(item_dir.glob(pattern) for pattern in IMAGE_PATTERNS):
            return True
    return False


def decide(now: datetime, root: Path, probability: int) -> str:
    """Return '', 'PUBLISH', or 'FORCE_PUBLISH'."""
    if probability < 1:
        raise ValueError("probability denominator must be >= 1")

    hour = now.hour
    if hour < 8 or hour > 23:
        return ""

    today = now.strftime("%Y-%m-%d")
    if not has_publishable_item(root, today):
        return ""

    if hour == 23:
        return "FORCE_PUBLISH"

    # 1/probability chance. Default probability=10 means 10%.
    return "PUBLISH" if random.randint(1, probability) == 1 else ""


def main() -> int:
    parser = argparse.ArgumentParser(description="Hourly gate for Xiaohongshu auto-publish cron.")
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="xiaohongshu-content root directory")
    parser.add_argument("--probability", type=int, default=10, help="publish chance denominator; 10 means 1/10")
    parser.add_argument("--now", help="override current time for tests, e.g. 2026-05-10T23:00:00+08:00")
    parser.add_argument("--verbose", action="store_true", help="print SKIP reason for manual debugging")
    args = parser.parse_args()

    if args.now:
        now = datetime.fromisoformat(args.now)
        if now.tzinfo is None:
            now = now.replace(tzinfo=TZ)
        else:
            now = now.astimezone(TZ)
    else:
        now = datetime.now(TZ)

    try:
        decision = decide(now, args.root, args.probability)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if decision:
        print(decision)
    elif args.verbose:
        print("SKIP")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
