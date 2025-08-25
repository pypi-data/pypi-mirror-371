from django.conf import settings
from django.test import TestCase
from django_mail_model_template.models import MailTemplate
from django_mail_model_template.utils import (
    get_mail_template,
    send_html_mail,
    send_text_mail,
)


class MailTemplateTest(TestCase):
    def test_get_main_template(self):
        MailTemplate.objects.create(
            name="main",
            subject="main subject {{ name }}",
            body="main body {% if name %}{{ name }}{% endif %}",
            html="<p>main html {{ name }}</p>",
            language="en",
        )
        params = {"name": "yamada"}
        result = get_mail_template("main", params, "en")
        self.assertEqual(result.subject, "main subject yamada")
        self.assertEqual(result.body, "main body yamada")
        self.assertEqual(result.html, "<p>main html yamada</p>")

    def test_send_html_mail(self):
        MailTemplate.objects.create(
            name="html_mail",
            subject="HTML subject {{ name }}",
            body="HTML body {% if name %}{{ name }}{% endif %}",
            html="<p>HTML {{ name }}</p>",
            language="en",
        )
        params = {"name": "yamada"}
        from_email = "from@example.com"
        to_email_list = ["to@example.com"]
        language = "en"
        with self.assertLogs("django_mail_model_template", level="INFO") as cm:
            send_html_mail("html_mail", params, from_email, to_email_list)
        send_html_mail("html_mail", params, from_email, to_email_list, language)

        self.assertIn("HTML subject yamada", cm.output[0])
        self.assertIn("<p>HTML yamada</p>", cm.output[0])

    def test_send_text_mail(self):
        MailTemplate.objects.create(
            name="text_mail",
            subject="Text subject {{ name }}",
            body="Text body {% if name %}{{ name }}{% endif %}",
            html="<p>Text {{ name }}</p>",
            language="en",
        )
        params = {"name": "yamada"}
        from_email = "from@example.com"
        to_email_list = ["to@example.com"]
        language = "en"

        with self.assertLogs("django_mail_model_template", level="INFO") as cm:
            send_text_mail(
                "text_mail",
                params,
                from_email,
                to_email_list,
                language,
            )

        self.assertIn("Text subject yamada", cm.output[0])
        self.assertIn("Text body yamada", cm.output[0])


class MailTemplateLanguageTests(TestCase):
    def setUp(self):
        # 英語（デフォルト）のテンプレート
        self.en_template = MailTemplate.objects.create(
            name="welcome",
            subject="Welcome {{ name }}",
            body="Hello {{ name }}, welcome to our service!",
            html="<p>Hello {{ name }}, welcome to our service!</p>",
            language="en",
        )

        # 日本語のテンプレート
        self.ja_template = MailTemplate.objects.create(
            name="welcome",
            subject="ようこそ {{ name }}さん",
            body="こんにちは、{{ name }}さん。当サービスへようこそ！",
            html="<p>こんにちは、{{ name }}さん。当サービスへようこそ！</p>",
            language="ja",
        )

    def test_default_language_behavior(self):
        # 言語を指定しない場合、settings.LANGUAGE_CODEが使われる
        params = {"name": "User"}
        result = get_mail_template("welcome", params)

        # 現在のsettings.LANGUAGE_CODEによって期待される結果が変わる
        if settings.LANGUAGE_CODE == "ja":
            self.assertEqual(result.subject, "ようこそ Userさん")
        else:
            # デフォルトはen、または他の言語でenにフォールバック
            self.assertEqual(result.subject, "Welcome User")

    def test_get_mail_template_with_language(self):
        # 日本語テンプレートを取得
        params = {"name": "山田"}
        result = get_mail_template("welcome", params, language="ja")
        self.assertEqual(result.subject, "ようこそ 山田さん")

    def test_language_fallback(self):
        # 存在しない言語（フランス語）を指定した場合、デフォルト言語にフォールバック
        params = {"name": "Pierre"}
        result = get_mail_template("welcome", params, language="fr")

        # settings.LANGUAGE_CODEがデフォルト
        expected_fallback = settings.LANGUAGE_CODE
        if expected_fallback not in ["en", "ja"]:
            expected_fallback = "en"  # 最終フォールバック

        if expected_fallback == "en":
            self.assertEqual(result.subject, "Welcome Pierre")
        else:
            self.assertEqual(result.subject, "ようこそ Pierreさん")
