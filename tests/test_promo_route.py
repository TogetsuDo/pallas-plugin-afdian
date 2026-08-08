from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import nonebot

ROOT = Path(__file__).resolve().parents[1]
_plugin = None


def load_afdian_plugin():
    global _plugin
    if _plugin is not None:
        return _plugin

    nonebot.init()
    with TemporaryDirectory() as temp_dir:
        package_root = Path(temp_dir) / "plugins"
        package_root.mkdir()
        plugin_path = package_root / "afdian"
        plugin_path.symlink_to(ROOT, target_is_directory=True)
        sys.path.insert(0, temp_dir)
        try:
            _plugin = nonebot.load_plugin("plugins.afdian")
        finally:
            sys.path.remove(temp_dir)
    return _plugin


def command_prefixes(menu_data):
    from pallas.core.platform.ingress.plugin_command_plaintext import (
        extract_command_prefixes_from_menu_data,
    )

    return extract_command_prefixes_from_menu_data(menu_data)


def test_promo_commands_are_declared_for_ingress_routing() -> None:
    plugin = load_afdian_plugin()

    assert plugin is not None
    menu_data = plugin.metadata.extra["menu_data"]
    promo_items = [
        item for item in menu_data if item.get("command_permission") == "afdian.promo"
    ]

    assert len(promo_items) == 1
    promo = promo_items[0]
    assert promo["trigger_condition"] == "牛牛爱发电 / 画画额度说明"
    prefixes = command_prefixes(menu_data)
    assert "牛牛爱发电" in prefixes
    assert "画画额度说明" in prefixes


def test_maintenance_commands_are_documented_and_routable() -> None:
    plugin = load_afdian_plugin()

    assert plugin is not None
    menu_data = plugin.metadata.extra["menu_data"]
    prefixes = command_prefixes(menu_data)

    assert "绑定画画共享额度" in prefixes
    assert "解绑画画共享额度" in prefixes
    assert "画画群绑定" in prefixes
    assert "画画群解绑" in prefixes
    assert "用户额度" in prefixes
    assert "用户额度设置" in prefixes
    assert any(
        item["trigger_condition"] == "用户额度设置 <qq> <n>" for item in menu_data
    )
