from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from pallas.api.config import install_hot_reload_config, repo_env_raw_value
from pallas.api.paths import plugin_data_dir


def _project_root() -> Path:
    # data/<plugin>/ → 仓库根
    return plugin_data_dir("afdian", create=False).parent.parent

try:
    from .money import normalize_money_key
except ImportError:
    from money import normalize_money_key


def _ui(label: str, *, group: str | None = None, secret: bool = False, hidden: bool = False) -> dict[str, Any]:
    extra: dict[str, Any] = {"label": label}
    if group:
        extra["ui_group"] = group
    if secret:
        extra["secret"] = True
    if hidden:
        extra["ui_hidden"] = True
    return extra


class Config(BaseModel, extra="ignore"):
    pallas_afdian_enabled: bool = Field(
        default=False,
        description="开启后，画画免费次数用尽时可使用额外额度。",
        json_schema_extra=_ui("启用爱发电额度", group="基础"),
    )
    pallas_afdian_webhook_token: str = Field(
        default="",
        description="爱发电后台 Webhook 校验 token，须与回调 URL 中的 token 一致。",
        json_schema_extra=_ui("Webhook Token", group="基础", secret=True),
    )
    pallas_afdian_default_credits: int = Field(
        default=10,
        ge=1,
        description="订单未命中方案映射时，发放的默认额外次数。",
        json_schema_extra=_ui("默认发放额度", group="额度方案"),
    )
    pallas_afdian_plan_credits_json: str = Field(
        default="",
        description='按方案 ID 发放额度，JSON 对象，如 {"plan_xxx": 30}。',
        json_schema_extra=_ui("方案额度 JSON", group="额度方案"),
    )
    pallas_afdian_plan_amount_credits_json: str = Field(
        default="",
        description="按方案 ID + 金额发放额度的嵌套 JSON；也可用下方文件路径。",
        json_schema_extra=_ui("方案金额额度 JSON", group="额度方案"),
    )
    pallas_afdian_plan_amount_credits_json_path: str = Field(
        default="",
        description="额度映射 JSON 文件路径；可用相对路径（会在 data/afdian、data/draw 等目录查找）。",
        json_schema_extra=_ui("方案金额额度文件", group="额度方案"),
    )
    pallas_afdian_promo_page_url: str = Field(
        default="",
        description="「牛牛爱发电」回复中的支持页链接。",
        json_schema_extra=_ui("支持页链接", group="宣传"),
    )
    pallas_afdian_promo_image_url: str = Field(
        default="",
        description="宣传图网络地址（http/https）；与本地配图二选一即可。",
        json_schema_extra=_ui("宣传图 URL", group="宣传"),
    )
    pallas_afdian_promo_image_path: str = Field(
        default="",
        description="宣传图本地路径或文件名（如 aifadian.jpg 或 data/draw/aifadian.jpg）；会在仓库根、data/afdian、data/draw、data/pallas_image 查找；按文件字节发送。",
        json_schema_extra=_ui("宣传图本地路径", group="宣传"),
    )
    pallas_afdian_group_billing_enabled: bool = Field(
        default=False,
        description="开启后，指定群可绑定共享额外额度。",
        json_schema_extra=_ui("启用群共享额度", group="群共享"),
    )
    pallas_afdian_group_billing_group_ids: list[int] = Field(
        default_factory=list,
        description="允许共享额度的群号白名单；开启总开关后仍须填群号，留空表示没有任何群可用。",
        json_schema_extra=_ui("共享额度群号列表", group="群共享"),
    )


def parse_env_value(name: str, raw: str, annotation: Any) -> Any:
    text = raw.strip()
    annotation_text = str(annotation).lower()
    if "bool" in annotation_text:
        return text.lower() in ("1", "true", "yes", "on")
    if "list" in annotation_text or "dict" in annotation_text:
        return json.loads(text) if text else []
    if "int" in annotation_text:
        return int(text)
    return text


def _legacy_value(name: str) -> str:
    value = repo_env_raw_value(name)
    return str(value).strip() if value is not None else ""


def _with_legacy_values(config: Config) -> Config:
    updates: dict[str, object] = {}
    for field_name in Config.model_fields:
        value = getattr(config, field_name)
        if value not in ("", False, [], 0):
            continue
        legacy_name = field_name.replace(
            "pallas_afdian_", "pallas_image_afdian_", 1
        ).upper()
        legacy = _legacy_value(legacy_name)
        if legacy:
            updates[field_name] = parse_env_value(
                field_name, legacy, Config.model_fields[field_name].annotation
            )
    if not config.pallas_afdian_webhook_token and "pallas_afdian_webhook_token" not in updates:
        token = _legacy_value("DRAW_AFDIAN_WEBHOOK_TOKEN")
        if token:
            updates["pallas_afdian_webhook_token"] = token
    return config.model_copy(update=updates)


def get_config() -> Config:
    return _with_legacy_values(plugin_webui.get())


def is_ready() -> bool:
    config = get_config()
    return config.pallas_afdian_enabled and bool(
        config.pallas_afdian_webhook_token.strip()
    )


def resolve_data_file(path_text: str) -> Path | None:
    """解析配置中的相对/绝对数据文件路径（兼容旧 data/draw）。"""
    text = (path_text or "").strip()
    if not text:
        return None
    root = _project_root()
    candidates: list[Path] = []
    raw = Path(text)
    if raw.is_absolute():
        candidates.append(raw)
    else:
        candidates.append(root / text)
        candidates.append(Path.cwd() / text)
        candidates.append(plugin_data_dir("afdian", create=False) / text)
        candidates.append(root / "data" / "draw" / text)
        candidates.append(root / "data" / "pallas_image" / text)
        if raw.name != text:
            candidates.append(plugin_data_dir("afdian", create=False) / raw.name)
            candidates.append(root / "data" / "draw" / raw.name)
    for path in candidates:
        if path.is_file():
            return path
    return None


def resolve_promo_image_path(config: Config | None = None) -> Path | None:
    cfg = config or get_config()
    return resolve_data_file(cfg.pallas_afdian_promo_image_path)


def plan_amount_credits(config: Config) -> dict[str, dict[str, int]]:
    raw = config.pallas_afdian_plan_amount_credits_json
    path = resolve_data_file(config.pallas_afdian_plan_amount_credits_json_path)
    if path is not None:
        raw = path.read_text(encoding="utf-8")
    try:
        source = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}
    result: dict[str, dict[str, int]] = {}
    if not isinstance(source, dict):
        return result
    for plan_id, entries in source.items():
        if not isinstance(entries, dict):
            continue
        mapped = {
            normalize_money_key(amount): int(credits)
            for amount, credits in entries.items()
            if normalize_money_key(amount) and isinstance(credits, int) and credits > 0
        }
        if mapped:
            result[str(plan_id).strip()] = mapped
    return result


def plan_credits(config: Config) -> dict[str, int]:
    try:
        source = json.loads(config.pallas_afdian_plan_credits_json or "{}")
    except json.JSONDecodeError:
        return {}
    if not isinstance(source, dict):
        return {}
    return {
        str(key).strip(): value
        for key, value in source.items()
        if isinstance(value, int) and value > 0
    }


plugin_webui = install_hot_reload_config(
    Config, config_module=__name__, parse_env_value=parse_env_value
)
