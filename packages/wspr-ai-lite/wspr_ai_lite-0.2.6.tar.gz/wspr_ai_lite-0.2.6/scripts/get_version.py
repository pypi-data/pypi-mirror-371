#!/usr/bin/env python3

from __future__ import annotations

"""Print the effective docs version:
1) package __version__ if importable
2) else latest git tag (without leading 'v')
3) else 'dev'
"""

import subprocess
import sys

def main() -> int:
    # 1) Try package version
    try:
        import wspr_ai_lite as m  # type: ignore
        v = getattr(m, "__version__", "").strip()
        if v:
            print(v)
            return 0
    except Exception:
        pass

    # 2) Try git tag
    try:
        v = subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0"],
            text=True,
        ).strip().lstrip("v")
        if v:
            print(v)
            return 0
    except Exception:
        pass

    # 3) Fallback
    print("dev")
    return 0

if __name__ == "__main__":
    sys.exit(main())
