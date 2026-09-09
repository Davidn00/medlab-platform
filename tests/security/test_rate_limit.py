from unittest.mock import MagicMock, patch

from app.core.rate_limit import (
    check_login_rate_limit,
    clear_login_rate_limit,
)


@patch("app.core.rate_limit.get_redis_client")
def test_login_rate_limit_allows_first_attempt(mock_get_redis):
    redis = MagicMock()

    redis.incr.return_value = 1

    mock_get_redis.return_value = redis

    assert check_login_rate_limit(
        "127.0.0.1:test@example.com"
    )

    redis.expire.assert_called_once()


@patch("app.core.rate_limit.get_redis_client")
def test_login_rate_limit_blocks_excess_attempts(
    mock_get_redis,
):
    redis = MagicMock()

    redis.incr.return_value = 6

    mock_get_redis.return_value = redis

    assert not check_login_rate_limit(
        "127.0.0.1:test@example.com"
    )


@patch("app.core.rate_limit.get_redis_client")
def test_clear_login_rate_limit(mock_get_redis):
    redis = MagicMock()

    mock_get_redis.return_value = redis

    clear_login_rate_limit(
        "127.0.0.1:test@example.com"
    )

    redis.delete.assert_called_once()