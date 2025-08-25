from django.test import TestCase
from django_mail_model_template.models import MailTemplate


class MailTemplateTest(TestCase):

    def setUp(self):
        # Setup code to create a MailTemplate instance for testing
        self.mail_template = MailTemplate.objects.create(
            name="Test Template",
            subject="Test Subject",
            body="This is a test body.",
            html="<p>This is a test HTML body.</p>",
            language="en",
        )

    def test_mail_template_creation(self):
        self.assertTrue(isinstance(self.mail_template, MailTemplate))
        self.assertEqual(
            self.mail_template.__str__(),
            f"{self.mail_template.name} ({self.mail_template.language})",
        )

    def test_mail_template_fields(self):
        self.assertEqual(self.mail_template.name, "Test Template")
        self.assertEqual(self.mail_template.subject, "Test Subject")
        self.assertEqual(self.mail_template.body, "This is a test body.")
        self.assertEqual(self.mail_template.html, "<p>This is a test HTML body.</p>")
        self.assertEqual(self.mail_template.language, "en")
