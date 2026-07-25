"""Public soft API for plugins that consume Afdian draw credits."""

try:
    from .config import is_ready as _is_ready
    from .group_billing import (
        group_billing_is_shared as _group_billing_is_shared,
    )
    from .group_billing import (
        group_uses_shared_billing as _group_uses_shared_billing,
    )
    from .group_billing import (
        resolve_billing_user_id as _resolve_billing_user_id,
    )
    from .store import (
        admin_set_balance as _admin_set_balance,
    )
    from .store import (
        credit_balance as _credit_balance,
    )
    from .store import (
        debit_one as _debit_one,
    )
    from .store import (
        ever_had_credits as _ever_had_credits,
    )
except ImportError:  # Supports direct module imports in lightweight tests.
    from group_billing import (
        group_billing_is_shared as _group_billing_is_shared,
    )
    from group_billing import (
        group_uses_shared_billing as _group_uses_shared_billing,
    )
    from group_billing import (
        resolve_billing_user_id as _resolve_billing_user_id,
    )
    from store import (
        admin_set_balance as _admin_set_balance,
    )
    from store import (
        credit_balance as _credit_balance,
    )
    from store import (
        debit_one as _debit_one,
    )
    from store import (
        ever_had_credits as _ever_had_credits,
    )

    from config import is_ready as _is_ready


def is_available() -> bool:
    return True


def is_ready() -> bool:
    return _is_ready()


def credit_balance(user_id: int) -> int:
    return _credit_balance(user_id)


def ever_had_credits(user_id: int) -> bool:
    return _ever_had_credits(user_id)


def resolve_billing_user_id(group_id: int, actor_user_id: int) -> int:
    return _resolve_billing_user_id(group_id, actor_user_id)


def group_billing_is_shared(group_id: int, actor_user_id: int) -> bool:
    return _group_billing_is_shared(group_id, actor_user_id)


def group_uses_shared_billing(group_id: int) -> bool:
    return _group_uses_shared_billing(group_id)


def group_billing_owner(group_id: int) -> int | None:
    try:
        from .group_billing import group_billing_owner as _owner
    except ImportError:
        from group_billing import group_billing_owner as _owner
    return _owner(group_id)


async def debit_one(user_id: int) -> None:
    await _debit_one(user_id)


async def admin_set_balance(user_id: int, balance: int) -> None:
    await _admin_set_balance(user_id, balance)


def quota_exhausted_message(
    *, limit_n: int, shared_pool: bool, ever_had: bool, has_owner: bool
) -> str:
    """中性拒画文案；不含口令广告。ever_had 预留站点自定义模板。"""
    del ever_had
    free_prefix = f"今日免费次数已用完（{limit_n} 次），" if limit_n > 0 else ""
    if shared_pool:
        if has_owner:
            return f"{free_prefix}本群共享额度不足。"
        return f"{free_prefix}本群尚未配置共享额度。"
    return f"{free_prefix}额外额度不足。"


def format_balance_text(balance: int) -> str:
    return f"剩余 {balance} 次" if balance > 0 else "无额外额度"


def extra_quota_label() -> str:
    return "额外额度"
