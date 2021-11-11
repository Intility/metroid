import asyncio

from django.core.management import call_command

import pytest


@pytest.mark.asyncio
async def mock_subscription_return(**kwargs):
    if kwargs.get('topic_name') == 'test-two':
        await asyncio.sleep(2)
    else:
        await asyncio.sleep(20)


@pytest.mark.asyncio
async def mock_subscription_exception(**kwargs):
    if kwargs.get('topic_name') == 'test-two':
        raise ValueError('Mocked error')
    else:
        await asyncio.sleep(20)


@pytest.fixture
def subscriptions_return(mocker):
    """
    Make one task exit quickly, while the rest runs for a long time.
    This triggers `return_when=asyncio.FIRST_COMPLETED`
    """
    mocker.patch('metroid.management.commands.metroid.subscribe_to_topic', mock_subscription_return)


@pytest.fixture
def subscriptions_exception(mocker):
    """
    Make one task exit quickly, while the rest runs for a long time.
    This triggers `return_when=asyncio.FIRST_COMPLETED`
    """
    mocker.patch('metroid.management.commands.metroid.subscribe_to_topic', mock_subscription_exception)


def test_command_early_return(subscriptions_return, caplog):
    with pytest.raises(SystemExit):
        call_command('metroid')
    assert [x for x in caplog.records if 'ended early without an exception' in x.message]
    assert [x for x in caplog.records if 'Cancelling pending task' in x.message]
    assert not [x for x in caplog.records if 'Exception in subscription' in x.message]
    assert [x for x in caplog.records if 'All tasks cancelled' in x.message]


def test_command_exception(subscriptions_exception, caplog):
    with pytest.raises(SystemExit):
        call_command('metroid')
    assert [x for x in caplog.records if 'Exception in subscription' in x.message]
    assert [x for x in caplog.records if 'Cancelling pending task' in x.message]
    assert not [x for x in caplog.records if 'ended early without an exception' in x.message]
    assert [x for x in caplog.records if 'All tasks cancelled' in x.message]
