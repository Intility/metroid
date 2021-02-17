from django.apps import AppConfig


class MetroidConfig(AppConfig):
    name = 'metroid'

    def ready(self) -> None:
        """
        Validate settings on app ready
        """
        from metroid.config import settings

        settings.validate()
