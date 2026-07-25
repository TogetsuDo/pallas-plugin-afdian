from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Query, Request
from nonebot import logger

from .config import get_config, is_ready, plan_amount_credits, plan_credits
from .money import normalize_money_key, resolve_order_credits
from .store import grant_order, parse_qq_from_remark, skip_order


def _ok() -> dict[str, int | str]:
    return {"ec": 200, "em": ""}


def register_webhook(app: FastAPI) -> None:
    async def handle(
        request: Request, token: str | None = Query(None)
    ) -> dict[str, int | str]:
        if not is_ready():
            raise HTTPException(
                status_code=404, detail="Afdian webhook 未启用或未配置 token"
            )
        config = get_config()
        if (token or "").strip() != config.pallas_afdian_webhook_token.strip():
            raise HTTPException(status_code=401, detail="token 无效")
        try:
            body: Any = await request.json()
        except Exception:
            logger.warning("Afdian webhook 非 JSON 请求体")
            return _ok()
        data = body.get("data") if isinstance(body, dict) else None
        order = (
            data.get("order")
            if isinstance(data, dict) and data.get("type") == "order"
            else None
        )
        if not isinstance(order, dict):
            return _ok()
        order_id = str(order.get("out_trade_no") or "").strip()
        if not order_id or int(order.get("status") or 0) != 2:
            return _ok()
        user_id = parse_qq_from_remark(str(order.get("remark") or ""))
        if user_id is None:
            await skip_order(order_id)
            logger.warning("Afdian 订单 {} 未包含有效 QQ", order_id)
            return _ok()
        amount = str(order.get("total_amount") or order.get("show_amount") or "")
        credits = resolve_order_credits(
            str(order.get("plan_id") or ""),
            amount,
            plan_amount_credits=plan_amount_credits(config),
            plan_only_credits=plan_credits(config),
            default_credits=config.pallas_afdian_default_credits,
        )
        if await grant_order(user_id, credits, order_id):
            logger.info(
                "Afdian 订单入账 order={} qq={} credits={} amount={}",
                order_id,
                user_id,
                credits,
                normalize_money_key(amount),
            )
        return _ok()

    app.post("/afdian/webhook")(handle)
    app.post("/pallas-image/afdian/webhook")(handle)
