from __future__ import annotations

import asyncio
import json
from pathlib import Path

from pallas.api.paths import plugin_data_dir

try:
    from .config import get_config
except ImportError:
    from config import get_config

STORE_FILENAME = "pallas_afdian_group_bindings.json"
_flush_lock = asyncio.Lock()


def bindings_path() -> Path:
    return plugin_data_dir("afdian") / STORE_FILENAME


def _read() -> dict[int, int]:
    path = bindings_path()
    if not path.is_file():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    bindings = payload.get("bindings", {}) if isinstance(payload, dict) else {}
    if not isinstance(bindings, dict):
        return {}
    return {
        int(group_id): int(owner_id)
        for group_id, owner_id in bindings.items()
        if str(group_id).isdigit()
        and str(owner_id).isdigit()
        and int(group_id) > 0
        and int(owner_id) > 0
    }


def _write(bindings: dict[int, int]) -> None:
    path = bindings_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "version": 1,
                "bindings": {str(key): value for key, value in bindings.items()},
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def group_uses_shared_billing(group_id: int) -> bool:
    config = get_config()
    if group_id <= 0 or not config.pallas_afdian_group_billing_enabled:
        return False
    group_ids = set(config.pallas_afdian_group_billing_group_ids)
    return not group_ids or group_id in group_ids


def group_billing_owner(group_id: int) -> int | None:
    return _read().get(group_id) if group_uses_shared_billing(group_id) else None


def resolve_billing_user_id(group_id: int, actor_user_id: int) -> int:
    return group_billing_owner(group_id) or actor_user_id


def group_billing_is_shared(group_id: int, actor_user_id: int) -> bool:
    owner = group_billing_owner(group_id)
    return owner is not None and owner != actor_user_id


async def bind_group(group_id: int, owner_user_id: int) -> None:
    if group_id <= 0 or owner_user_id <= 0:
        raise ValueError("group_id and owner_user_id must be positive")
    async with _flush_lock:
        bindings = await asyncio.to_thread(_read)
        bindings[group_id] = owner_user_id
        await asyncio.to_thread(_write, bindings)


async def unbind_group(group_id: int) -> bool:
    async with _flush_lock:
        bindings = await asyncio.to_thread(_read)
        if group_id not in bindings:
            return False
        del bindings[group_id]
        await asyncio.to_thread(_write, bindings)
        return True
