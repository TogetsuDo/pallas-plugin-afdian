from __future__ import annotations

from nonebot import logger
from nonebot.adapters.onebot.v11 import GroupMessageEvent, Message, MessageSegment

from pallas.api.commands import (
    PluginHandlerContext,
    bind_alias_handlers,
    message_command,
)
from pallas.api.platform import try_acquire_group_broadcast_slot

from .api import format_balance_text
from .config import get_config, resolve_promo_image_path
from .group_billing import (
    bind_group,
    group_billing_is_shared,
    group_billing_owner,
    group_uses_shared_billing,
    resolve_billing_user_id,
    unbind_group,
)
from .store import admin_set_balance, credit_balance, ever_had_credits

promo = message_command(
    "afdian.promo", "牛牛爱发电", aliases=("画画额度说明",), cd_sec=10
)
quota = message_command("afdian.quota", "画画额度", cd_sec=5)
group_bind = message_command(
    "afdian.group_bind", "绑定画画共享额度", scene="group", cd_sec=10
)
group_unbind = message_command(
    "afdian.group_unbind", "解绑画画共享额度", scene="group", cd_sec=10
)
group_admin_bind = message_command(
    "afdian.group_admin", "画画群绑定", scene="private", cd_sec=5
)
group_admin_unbind = message_command(
    "afdian.group_admin", "画画群解绑", scene="private", cd_sec=5
)
user_quota = message_command("afdian.user_quota", "用户额度", scene="private", cd_sec=5)
user_quota_set = message_command(
    "afdian.user_quota_set", "用户额度设置", scene="private", cd_sec=5
)


def _args(context: PluginHandlerContext, command: str) -> list[str]:
    text = context.plain_text.strip()
    return text[len(command) :].strip().split() if text.startswith(command) else []


async def handle_promo(context: PluginHandlerContext) -> None:
    if isinstance(context.event, GroupMessageEvent):
        if not await try_acquire_group_broadcast_slot(
            "afdian.promo", context.event.group_id
        ):
            return
    config = get_config()
    message = Message()
    local_image = resolve_promo_image_path(config)
    if local_image is not None:
        message += MessageSegment.image(f"file://{local_image.resolve()}")
    elif config.pallas_afdian_promo_image_url.strip():
        message += MessageSegment.image(config.pallas_afdian_promo_image_url.strip())
    page = config.pallas_afdian_promo_page_url.strip()
    if page:
        if message:
            message += "\n"
        message += page
    if not message:
        await context.finish("页面暂未配置，请联系管理员。")
    await context.finish(message)


async def handle_quota(context: PluginHandlerContext) -> None:
    group_id = context.group_id or 0
    actor_id = int(context.user_id)
    billing_id = resolve_billing_user_id(group_id, actor_id)
    balance = format_balance_text(credit_balance(billing_id))
    if group_billing_is_shared(group_id, actor_id):
        await context.finish(f"本群共享额度（QQ {billing_id}）：{balance}")
    elif group_uses_shared_billing(group_id):
        await context.finish(f"本群共享额度尚未绑定；你的额外额度：{balance}")
    else:
        await context.finish(f"你的额外额度：{balance}")


async def handle_group_bind(context: PluginHandlerContext) -> None:
    group_id = context.group_id
    if group_id is None:
        await context.finish("请在群内使用此命令。")
    if not group_uses_shared_billing(group_id):
        await context.finish("本群未启用共享额度。")
    actor_id = int(context.user_id)
    owner = group_billing_owner(group_id)
    if owner is not None and owner != actor_id:
        await context.finish(f"本群已绑定 QQ {owner}。")
    if credit_balance(actor_id) < 1 and not ever_had_credits(actor_id):
        await context.finish("请先获得额外额度后再绑定。")
    await bind_group(group_id, actor_id)
    logger.info("Afdian group billing bound group={} owner={}", group_id, actor_id)
    await context.finish(f"已绑定本群共享额度至 QQ {actor_id}。")


async def handle_group_unbind(context: PluginHandlerContext) -> None:
    group_id = context.group_id
    if group_id is None:
        await context.finish("请在群内使用此命令。")
    owner = group_billing_owner(group_id)
    if owner is None:
        await context.finish("本群尚未绑定共享额度。")
    if owner != int(context.user_id):
        await context.finish("仅绑定人可解绑。")
    await unbind_group(group_id)
    await context.finish("已解除本群共享额度绑定。")


async def handle_group_admin_bind(context: PluginHandlerContext) -> None:
    args = _args(context, "画画群绑定")
    if len(args) != 2 or not all(value.isdigit() for value in args):
        await context.finish("用法：画画群绑定 <gid> <qq>")
    group_id, owner_id = map(int, args)
    if not group_uses_shared_billing(group_id):
        await context.finish("该群未启用共享额度。")
    await bind_group(group_id, owner_id)
    await context.finish(f"已将群 {group_id} 绑定到 QQ {owner_id}。")


async def handle_group_admin_unbind(context: PluginHandlerContext) -> None:
    args = _args(context, "画画群解绑")
    if len(args) != 1 or not args[0].isdigit():
        await context.finish("用法：画画群解绑 <gid>")
    group_id = int(args[0])
    await context.finish(
        f"已{'解除' if await unbind_group(group_id) else '确认未存在'}群 {group_id} 的共享额度绑定。"
    )


async def handle_user_quota(context: PluginHandlerContext) -> None:
    args = _args(context, "用户额度")
    if len(args) != 1 or not args[0].isdigit():
        await context.finish("用法：用户额度 <qq>")
    user_id = int(args[0])
    await context.finish(
        f"QQ {user_id}：{format_balance_text(credit_balance(user_id))}"
    )


async def handle_user_quota_set(context: PluginHandlerContext) -> None:
    args = _args(context, "用户额度设置")
    if len(args) != 2 or not args[0].isdigit():
        await context.finish("用法：用户额度设置 <qq> <n>")
    try:
        balance = int(args[1])
    except ValueError:
        await context.finish("额度须为整数。")
    await admin_set_balance(int(args[0]), balance)
    await context.finish(f"已设置 QQ {args[0]} 的额外额度为 {balance} 次。")


bind_alias_handlers(promo, handle_promo)
bind_alias_handlers(quota, handle_quota)
bind_alias_handlers(group_bind, handle_group_bind)
bind_alias_handlers(group_unbind, handle_group_unbind)
bind_alias_handlers(group_admin_bind, handle_group_admin_bind)
bind_alias_handlers(group_admin_unbind, handle_group_admin_unbind)
bind_alias_handlers(user_quota, handle_user_quota)
bind_alias_handlers(user_quota_set, handle_user_quota_set)
