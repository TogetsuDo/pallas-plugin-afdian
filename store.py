from __future__ import annotations

import asyncio
import json
import os
import re
import threading
from contextlib import contextmanager
from pathlib import Path

from nonebot import logger

from pallas.api.paths import plugin_data_dir

STORE_FILENAME = "pallas_afdian_credits.json"
_lock = threading.Lock()
_flush_lock = asyncio.Lock()
_credits: dict[int, int] = {}
_orders: set[str] = set()
_ever_credited: set[int] = set()
_loaded_mtime_ns = 0


def credits_path() -> Path:
    return plugin_data_dir("afdian") / STORE_FILENAME


def _mtime(path: Path) -> int:
    try:
        return path.stat().st_mtime_ns
    except OSError:
        return 0


@contextmanager
def interprocess_lock():
    path = credits_path().with_suffix(".json.lock")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(path, os.O_CREAT | os.O_RDWR)
    try:
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _load() -> None:
    global _credits, _orders, _ever_credited, _loaded_mtime_ns
    path = credits_path()
    if not path.is_file():
        _credits, _orders, _ever_credited, _loaded_mtime_ns = {}, set(), set(), 0
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        logger.warning("无法读取 Afdian 额度数据: {}", error)
        return
    if not isinstance(data, dict):
        return
    _credits = {int(key): int(value) for key, value in data.get("credits", {}).items()}
    _orders = {str(value) for value in data.get("processed_orders", [])}
    _ever_credited = {int(value) for value in data.get("ever_credited_users", [])}
    _loaded_mtime_ns = _mtime(path)


def _reload_if_needed() -> None:
    if _mtime(credits_path()) != _loaded_mtime_ns:
        _load()


def _save() -> None:
    global _loaded_mtime_ns
    path = credits_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".json.tmp")
    temp.write_text(
        json.dumps(
            {
                "version": 2,
                "credits": {
                    str(key): value for key, value in _credits.items() if value
                },
                "processed_orders": sorted(_orders),
                "ever_credited_users": sorted(_ever_credited),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    temp.replace(path)
    _loaded_mtime_ns = _mtime(path)


def credit_balance(user_id: int) -> int:
    with _lock:
        _reload_if_needed()
        return _credits.get(user_id, 0)


def ever_had_credits(user_id: int) -> bool:
    with _lock:
        _reload_if_needed()
        return user_id in _ever_credited


async def _mutate(work) -> bool:
    def locked_work() -> bool:
        with interprocess_lock(), _lock:
            _load()
            changed = work()
            if changed:
                _save()
            return changed

    async with _flush_lock:
        return await asyncio.to_thread(locked_work)


async def debit_one(user_id: int) -> None:
    await _mutate(
        lambda: _credits.__setitem__(user_id, _credits.get(user_id, 0) - 1) is None
    )


async def admin_set_balance(user_id: int, balance: int) -> None:
    def work() -> bool:
        if balance:
            _credits[user_id] = balance
            if balance > 0:
                _ever_credited.add(user_id)
        else:
            _credits.pop(user_id, None)
        return True

    await _mutate(work)


async def grant_order(user_id: int, credits: int, order_id: str) -> bool:
    if credits < 1 or not order_id:
        return False

    def work() -> bool:
        if order_id in _orders:
            return False
        _orders.add(order_id)
        _credits[user_id] = _credits.get(user_id, 0) + credits
        _ever_credited.add(user_id)
        return True

    return await _mutate(work)


async def skip_order(order_id: str) -> None:
    if order_id:
        await _mutate(
            lambda: False if order_id in _orders else (_orders.add(order_id) is None)
        )


_remark_qq = re.compile(r"(?:qq|ＱＱ)\s*[:：]?\s*(\d{5,12})", re.IGNORECASE)
_remark_digits = re.compile(r"(?<!\d)(\d{5,12})(?!\d)")


def parse_qq_from_remark(remark: str) -> int | None:
    match = _remark_qq.search(remark or "") or _remark_digits.search(remark or "")
    return int(match.group(1)) if match else None
