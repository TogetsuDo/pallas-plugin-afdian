"""Afdian order amount and credit mapping helpers."""

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation


def normalize_money_key(raw: object) -> str:
    text = str(raw or "").strip()
    if not text:
        return ""
    try:
        return format(
            Decimal(text).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), "f"
        )
    except InvalidOperation:
        return text


def resolve_order_credits(
    plan_id: str,
    amount_raw: str,
    *,
    plan_amount_credits: dict[str, dict[str, int]],
    plan_only_credits: dict[str, int],
    default_credits: int,
) -> int:
    plan_id = plan_id.strip()
    amount_key = normalize_money_key(amount_raw)
    if plan_id and amount_key:
        by_amount = plan_amount_credits.get(plan_id, {})
        if amount_key in by_amount:
            return by_amount[amount_key]
    return plan_only_credits.get(plan_id, default_credits)
