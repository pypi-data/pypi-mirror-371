from django.db import models
from django.conf import settings


class MailTemplate(models.Model):
    name = models.CharField(max_length=255)
    language = models.CharField(
        max_length=10, default="ja"
    )  # ISO 639-1/IETF
    subject = models.CharField(max_length=255)
    body = models.TextField()
    html = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("name", "language")
        indexes = [
            models.Index(fields=["name", "language"]),
        ]

    def __str__(self):
        return f"{self.name} ({self.language})"
