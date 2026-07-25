import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from api import quota_exhausted_message


def test_quota_messages_are_neutral() -> None:
    messages = (
        quota_exhausted_message(
            limit_n=3, shared_pool=True, ever_had=False, has_owner=False
        ),
        quota_exhausted_message(
            limit_n=3, shared_pool=True, ever_had=True, has_owner=True
        ),
        quota_exhausted_message(
            limit_n=3, shared_pool=False, ever_had=True, has_owner=False
        ),
        quota_exhausted_message(
            limit_n=0, shared_pool=False, ever_had=False, has_owner=False
        ),
    )

    for text in messages:
        assert "爱发电" not in text
        assert "牛牛爱发电" not in text
        assert "获取赞助" not in text
        assert "赞助" not in text

    assert messages[0] == "今日免费次数已用完（3 次），本群尚未配置共享额度。"
    assert messages[1] == "今日免费次数已用完（3 次），本群共享额度不足。"
    assert messages[2] == "今日免费次数已用完（3 次），额外额度不足。"
    assert messages[3] == "额外额度不足。"
