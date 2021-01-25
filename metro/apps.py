from django.apps import AppConfig


class MetroConfig(AppConfig):
    name = 'metro'

    def ready(self) -> None:
        """
        In order to avoid circular imports we import signals here.
        """
        from metro.config import settings

        settings.validate()
