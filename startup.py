from shutil import copy2

from nonebot import logger

from pallas.api.paths import plugin_data_dir

_FILES = ("pallas_afdian_credits.json", "pallas_afdian_group_bindings.json")


def migrate_draw_data() -> None:
    destination_dir = plugin_data_dir("afdian")
    source_dir = plugin_data_dir("draw", create=False)
    for filename in _FILES:
        destination = destination_dir / filename
        source = source_dir / filename
        if destination.exists() or not source.is_file():
            continue
        try:
            copy2(source, destination)
            logger.info("已迁移 draw Afdian 数据文件: {}", filename)
        except OSError as error:
            logger.warning("迁移 draw Afdian 数据文件失败 {}: {}", filename, error)


def setup_afdian_runtime() -> None:
    migrate_draw_data()
    from nonebot import get_app

    from .webhook import register_webhook

    register_webhook(get_app())


def _register_startup() -> None:
    try:
        from nonebot import get_driver
    except Exception:
        return
    try:
        get_driver().on_startup(setup_afdian_runtime)
    except ValueError:
        # 单测等未 init NoneBot 的环境跳过挂载
        return


_register_startup()
