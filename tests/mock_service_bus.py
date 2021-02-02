import asyncio
import json


class Message:
    def __init__(self, i, **kwargs):
        self.error = kwargs.get('error', False)
        print(f'{self.error=}')
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
        await asyncio.sleep(1)
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

    @staticmethod
    def get_subscription_receiver(topic_name, subscription_name):
        if topic_name == 'error':
            return ReceiverMock(error=True)
        return ReceiverMock()
