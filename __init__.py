from nonebot.plugin import PluginMetadata

from pallas.api.metadata import (
    PLUGIN_EXTRA_VERSION,
    PLUGIN_HOMEPAGE,
    PLUGIN_MENU_TEMPLATE,
    SCENE_BOTH,
    SCENE_GROUP,
    SCENE_PRIVATE,
    join_usage,
    usage_line,
)
from pallas.api.platform import llm_command_tool_row

from . import handlers as handlers  # noqa: F401
from . import startup as startup  # noqa: F401

PLUGIN_ID = "afdian"

__plugin_meta__ = PluginMetadata(
    name="牛牛爱发电",
    description="通过爱发电为画画等功能提供可选额外额度。",
    usage=join_usage(
        usage_line("牛牛爱发电 / 画画额度说明", "查看额外额度支持页面"),
        usage_line("画画额度 / 画画次数", "查看额外额度或本群共享额度"),
        usage_line("绑定画画共享额度 / 解绑画画共享额度", "群内绑定或解除共享额度"),
        usage_line("画画群绑定 <gid> <qq> / 画画群解绑 <gid>", "私聊维护群共享额度"),
        usage_line("用户额度 <qq>", "私聊查看用户额外额度"),
        usage_line("用户额度设置 <qq> <n>", "私聊设置用户额外额度"),
    ),
    type="application",
    homepage=PLUGIN_HOMEPAGE,
    supported_adapters={"~onebot.v11"},
    extra={
        "help_tag": "tool",
        "version": "0.1.10",
        "menu_template": PLUGIN_MENU_TEMPLATE,
        "command_permissions": [
            {"id": "afdian.promo", "label": "牛牛爱发电", "default": "everyone"},
            {
                "id": "afdian.quota",
                "label": "画画额度 / 画画次数",
                "default": "everyone",
            },
            {
                "id": "afdian.group_bind",
                "label": "绑定画画共享额度",
                "default": "everyone",
            },
            {
                "id": "afdian.group_unbind",
                "label": "解绑画画共享额度",
                "default": "everyone",
            },
            {
                "id": "afdian.group_admin",
                "label": "画画群绑定与解绑",
                "default": "superuser",
            },
            {"id": "afdian.user_quota", "label": "用户额度", "default": "superuser"},
            {
                "id": "afdian.user_quota_set",
                "label": "用户额度设置",
                "default": "superuser",
            },
        ],
        "llm_tools": [
            llm_command_tool_row(
                name="afdian.quota",
                command_id="afdian.quota",
                description="查询画画额外额度或本群共享额度。用户问额度、画画次数时使用。",
                parameters={"type": "object", "properties": {}},
                command_template="画画额度",
                hints=["额度", "画画次数", "画画额度", "还有几次"],
            ),
            llm_command_tool_row(
                name="afdian.promo",
                command_id="afdian.promo",
                description="查看爱发电支持/额度说明页面。",
                parameters={"type": "object", "properties": {}},
                command_template="牛牛爱发电",
                hints=["爱发电", "支持一下", "赞助"],
            ),
        ],
        "menu_data": [
            {
                "func": "牛牛爱发电",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_BOTH,
                "trigger_condition": "牛牛爱发电 / 画画额度说明",
                "command_permission": "afdian.promo",
                "brief_des": "查看额外额度支持页面",
                "detail_des": "回复支持页面链接与宣传图。",
            },
            {
                "func": "画画额度",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_BOTH,
                "trigger_condition": "画画额度 / 画画次数",
                "command_permission": "afdian.quota",
                "brief_des": "查看额外额度",
                "detail_des": "群启用共享额度且已绑定时，显示共享额度。也可发「画画次数」。",
            },
            {
                "func": "群共享额度",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_GROUP,
                "trigger_condition": "绑定画画共享额度 / 解绑画画共享额度",
                "command_permissions": ["afdian.group_bind", "afdian.group_unbind"],
                "brief_des": "绑定或解除本群共享额度",
                "detail_des": "仅启用且在白名单内的群可绑定；绑定人须有或曾有额外额度，且仅绑定人可解绑。",
            },
            {
                "func": "共享额度维护",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_PRIVATE,
                "trigger_condition": "画画群绑定 <gid> <qq> / 画画群解绑 <gid>",
                "command_permission": "afdian.group_admin",
                "brief_des": "维护指定群的共享额度绑定",
                "detail_des": "目标群须启用共享额度并在白名单内。",
            },
            {
                "func": "用户额度查询",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_PRIVATE,
                "trigger_condition": "用户额度 <qq>",
                "command_permission": "afdian.user_quota",
                "brief_des": "查看用户额外额度",
                "detail_des": "返回指定 QQ 的当前余额。",
            },
            {
                "func": "用户额度设置",
                "trigger_method": "on_command",
                "trigger_scene": SCENE_PRIVATE,
                "trigger_condition": "用户额度设置 <qq> <n>",
                "command_permission": "afdian.user_quota_set",
                "brief_des": "设置用户额外额度",
                "detail_des": "将指定 QQ 的余额设为整数次数。",
            },
        ],
        "reload_policy": "metadata",
        "upstream_version": PLUGIN_EXTRA_VERSION,
    },
)
