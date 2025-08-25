from django_mail_model_template.admin import MailTemplateAdmin

from django.test import TestCase
from django_mail_model_template.models import MailTemplate
from django_mail_model_template.admin import MailTemplateAdmin
from django.contrib.admin.sites import AdminSite
from django.conf import settings

from django_mail_model_template.utils import get_mail_template


class MockRequest:
    pass


class MailTemplateAdminTests(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.mail_template_admin = MailTemplateAdmin(MailTemplate, self.site)

    def test_save_model(self):
        template = MailTemplate(
            name="Test Template",
            subject="Test Subject",
            body="Test Body",
            language=settings.LANGUAGE_CODE,
        )
        request = MockRequest()
        self.mail_template_admin.save_model(request, template, None, None)
        self.assertEqual(MailTemplate.objects.count(), 1)
        saved_template = MailTemplate.objects.first()
        self.assertEqual(saved_template.name, "Test Template")
        self.assertEqual(saved_template.subject, "Test Subject")
        self.assertEqual(saved_template.body, "Test Body")

    def test_delete_model(self):
        template = MailTemplate.objects.create(
            name="Test Template",
            subject="Test Subject",
            body="Test Body",
            language=settings.LANGUAGE_CODE,
        )
        request = MockRequest()
        self.mail_template_admin.delete_model(request, template)
        self.assertEqual(MailTemplate.objects.count(), 0)
