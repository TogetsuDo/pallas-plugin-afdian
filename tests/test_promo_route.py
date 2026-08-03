from pathlib import Path
import sys
from tempfile import TemporaryDirectory

import nonebot

from pallas.core.platform.ingress.plugin_command_plaintext import (
    extract_command_prefixes_from_menu_data,
)

ROOT = Path(__file__).resolve().parents[1]


def test_promo_commands_are_declared_for_ingress_routing() -> None:
    nonebot.init()
    with TemporaryDirectory() as temp_dir:
        package_root = Path(temp_dir) / "plugins"
        package_root.mkdir()
        plugin_path = package_root / "afdian"
        plugin_path.symlink_to(ROOT, target_is_directory=True)
        sys.path.insert(0, temp_dir)
        try:
            plugin = nonebot.load_plugin("plugins.afdian")
        finally:
            sys.path.remove(temp_dir)

    assert plugin is not None
    menu_data = plugin.metadata.extra["menu_data"]
    promo_items = [
        item for item in menu_data if item.get("command_permission") == "afdian.promo"
    ]

    assert len(promo_items) == 1
    promo = promo_items[0]
    assert promo["trigger_condition"] == "牛牛爱发电 / 画画额度说明"
    prefixes = extract_command_prefixes_from_menu_data(menu_data)
    assert "牛牛爱发电" in prefixes
    assert "画画额度说明" in prefixes
