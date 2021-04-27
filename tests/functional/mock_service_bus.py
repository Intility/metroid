import asyncio
import json
from unittest.mock import AsyncMock, MagicMock


class Message:
    def __init__(self, i, **kwargs):
        self.error = kwargs.get('error', False)
        self.i = i
        if self.i == 0:
            self.message = {
                'eventType': 'Intility.Jonas.Testing',
                'eventTime': '2021-02-02T12:50:39.611290+00:00',
                'dataVersion': '1.0',
                'data': f'Mocked - Yo, Metro is awesome',
                'subject': 'Test/Django/Module',
            }
        elif self.i == 1:
            self.message = {
                'eventType': 'Intility.Jonas.Testing',
                'eventTime': '2021-02-02T12:50:39.611290+00:00',
                'dataVersion': '1.0',
                'data': {'content': 'Mocked - Yo, Metro is awesome'},
                'subject': 'Exception/Django/Module',
            }
        else:
            self.message = {
                'eventType': 'Intility.Jonas.Testing',
                'eventTime': '2021-02-02T12:50:39.611290+00:00',
                'dataVersion': '1.0',
                'data': {'content': 'Mocked - Yo, Metro is awesome'},
                'subject': 'Ignore me',
            }

    @property
    def sequence_number(self):
        return self.i

    def __str__(self):
        if not self.error:
            return json.dumps(self.message)
        else:
            return str(self.message)  # Not something we can json.loads()


class ReceiverMock:
    def __init__(self, *args, **kwargs):
        self.error = kwargs.get('error', False)
        self.i = 0

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    async def __anext__(self):
        """
        Returns something 5 times with a 1 sec sleep in between each one
        """
        i = self.i
        if i >= 5:
            raise StopAsyncIteration
        self.i += 1
        await asyncio.sleep(0.2)
        if i == 4 and self.error:
            return Message(4, error=True)
        return Message(i)

    def __aiter__(self):
        return self

    async def complete_message(self, message):
        return True


class ServiceBusMock:
    def __init__(self, *args, **kwargs):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return None

    @classmethod
    def from_connection_string(cls, conn_str, transport_type):
        return cls(conn_str, transport_type)

    def get_subscription_receiver(self, topic_name, subscription_name):
        if topic_name == 'error':
            return AsyncMock(ReceiverMock(error=True))
        return AsyncMock(ReceiverMock())


# Create MagicMock with specs of our instances
# If this is confusing, it's because it is - and it's not really documented.
# https://bugs.python.org/issue40406
def instance_service_mock_ok() -> ServiceBusMock:
    service_mock = MagicMock()
    service_mock.configure_mock(
        **{
            'from_connection_string.return_value.__aenter__.return_value': MagicMock(
                ServiceBusMock(), **{'get_subscription_receiver.return_value.__aenter__.return_value': ReceiverMock()}
            )
        }
    )
    return service_mock


def instance_service_mock_error() -> ServiceBusMock:
    service_mock_error = MagicMock()
    service_mock_error.configure_mock(
        **{
            'from_connection_string.return_value.__aenter__.return_value': MagicMock(
                ServiceBusMock(),
                **{'get_subscription_receiver.return_value.__aenter__.return_value': ReceiverMock(error=True)},
            )
        }
    )
    return service_mock_error
