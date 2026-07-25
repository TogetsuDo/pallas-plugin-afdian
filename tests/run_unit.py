#!/usr/bin/env python3
"""不依赖 pytest Package 收集（仓库目录名含连字符）。"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from money import normalize_money_key, resolve_order_credits  # noqa: E402
from api import quota_exhausted_message  # noqa: E402


def main() -> None:
    assert normalize_money_key("1.2") == "1.20"
    assert (
        resolve_order_credits(
            "plan-a",
            "1.2",
            plan_amount_credits={"plan-a": {"1.20": 8}},
            plan_only_credits={"plan-a": 5},
            default_credits=1,
        )
        == 8
    )
    text = quota_exhausted_message(
        limit_n=3, shared_pool=False, ever_had=True, has_owner=False
    )
    assert "赞助" not in text and "爱发电" not in text
    print("unit checks passed")


if __name__ == "__main__":
    main()
