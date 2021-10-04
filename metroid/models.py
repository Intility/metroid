from django.db.models import CharField, DateTimeField, JSONField, Model, TextField


class FailedMessage(Model):
    created = DateTimeField(auto_now_add=True)
    topic_name = CharField(max_length=255)
    subscription_name = CharField(max_length=255)
    subject = CharField(max_length=255)
    message = JSONField()

    exception_str = TextField()
    traceback = TextField()

    # If there is a correlation ID (Requires Django GUID + Celery Integration), save it. Makes fetching logs easy
    correlation_id = CharField(max_length=36, blank=True)

    def __str__(self) -> str:
        """
        String representation
        """
        return f'{self.topic_name}-{self.subject}. Correlation ID: {self.correlation_id}'  # pragma: no cover


class FailedPublishMessage(Model):
    topic_name = CharField(max_length=255)
    event_type = CharField(max_length=255)
    subject = CharField(max_length=255)
    data_version = CharField(max_length=255)
    event_time = DateTimeField()
    data = JSONField()
    correlation_id = CharField(max_length=36, blank=True)

    def __str__(self) -> str:
        """
        String representation
        """
        return f'{self.topic_name}-{self.subject}. Correlation ID: {self.correlation_id}'  # pragma: no cover
