import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from money import normalize_money_key, resolve_order_credits


def test_normalize_money_key() -> None:
    assert normalize_money_key("1.2") == "1.20"
    assert normalize_money_key(" 2 ") == "2.00"
    assert normalize_money_key("invalid") == "invalid"
    assert normalize_money_key("") == ""


def test_resolve_credits_prefers_plan_amount_then_plan_then_default() -> None:
    kwargs = {
        "plan_amount_credits": {"plan-a": {"1.20": 8}},
        "plan_only_credits": {"plan-a": 5, "plan-b": 3},
        "default_credits": 1,
    }

    assert resolve_order_credits("plan-a", "1.2", **kwargs) == 8
    assert resolve_order_credits("plan-a", "9", **kwargs) == 5
    assert resolve_order_credits("plan-b", "9", **kwargs) == 3
    assert resolve_order_credits("unknown", "9", **kwargs) == 1
