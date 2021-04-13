import pytest
from redislite import Redis


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    monkeypatch.setattr('django_rq.queues.get_redis_connection', lambda _, strict: Redis('/tmp/test.rdb'))
