import factory
from factory.django import DjangoModelFactory
from .models import MailTemplate


class MailTemplateFactory(DjangoModelFactory):
    class Meta:
        model = MailTemplate

    name = factory.Faker("word")
    subject = factory.Faker("word")
    body = factory.Faker("text")
    html = factory.Faker("text")