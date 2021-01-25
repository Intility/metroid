from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView


class Metro(APIView):
    def get(self, request: Request) -> Response:
        """
        Fetches deferred messages
        """
        pass

    def post(self, request: Request) -> Response:
        """
        Retries a deferred message
        """
        pass
