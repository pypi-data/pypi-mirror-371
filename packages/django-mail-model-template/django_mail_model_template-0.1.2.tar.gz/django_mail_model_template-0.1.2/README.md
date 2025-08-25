# INSTALL

```shell
pip install django-mail-model-template
```

# Django settings

```python
INSTALLED_APPS = [
    ...
    'django_mail_model_template',
]
```

# Migrations

Migrations are a way of propagating changes you make to your models (adding a field, deleting a model, etc.) into your
database schema. They are designed to be mostly automatic, but you'll need to know when to make migrations, when to run
them, and the common issues you might run into.

You can create migrations for your application using the following command:

```shell
python manage.py makemigrations
```

This command will detect changes made to your models and generate the appropriate migrations.

Once the migrations have been created, you can apply them to your database using:

```shell
python manage.py migrate
```

This command applies the migrations and updates the database schema.

# Viewing Migrations in the Admin

Django's admin interface allows you to view the state of applied migrations. To do this, follow these steps:

1. Log in to the Django admin interface.
2. Navigate to the **"Migrations"** section, which is available under the "Django" admin area.
3. Here, you will be able to see a list of migrations and their states (applied or unapplied).

By using these tools, you can manage the evolution of your database schema in a controlled and predictable way.

# Usage

Register the template either via django-admin or through code.

```python
from django_mail_model_template.models import MailTemplate

MailTemplate.objects.create(
    name="main",
    subject="main subject {{ name }}",
    body="main body {% if name %}{{ name }}{% endif %}",
    html="<p>main html {{ name }}</p>",
)
```

```python
from django_mail_model_template.utils import get_mail_template
params = {"name": "yamada"}
result = get_mail_template("main", params)
```

## send html mail

```python
from django_mail_model_template.utils import send_html_mail
params = {"name": "yamada"}
send_html_mail("main", params, "from@example.com",["to@example.com"])
```

## send text mail

```python
from django_mail_model_template.utils import send_text_mail
params = {"name": "yamada"}
send_text_mail("main", params, "from@example.com",["to@example.com"])
```

# Multi-language Support

## Setting up templates for different languages

You can create templates for different languages by specifying the `language` field:

```python
from django_mail_model_template.models import MailTemplate

# English template
MailTemplate.objects.create(
    name="welcome",
    subject="Welcome {{ name }}",
    body="Hello {{ name }}, welcome to our service!",
    html="<p>Hello {{ name }}, welcome to our service!</p>",
    language="en"  # ISO 639-1 language code
)

# Japanese template
MailTemplate.objects.create(
    name="welcome",
    subject="ようこそ {{ name }}さん",
    body="こんにちは、{{ name }}さん。当サービスへようこそ！",
    html="<p>こんにちは、{{ name }}さん。当サービスへようこそ！</p>",
    language="ja"
)
```

## Using templates with language specification

You can specify the language when retrieving templates:

```python
from django_mail_model_template.utils import get_mail_template

# Get template in English
params = {"name": "John"}
result = get_mail_template("welcome", params, language="en")

# Get template in Japanese
params = {"name": "山田"}
result = get_mail_template("welcome", params, language="ja")
```

If a template is not available in the specified language, it will fall back to the default language (as specified in `settings.LANGUAGE_CODE`), or to English if that's not available.

# Important Note About Return Values

As of version X.X.X, `get_mail_template()` now returns a `MailTemplateParams` object instead of a dictionary. Access the values using attribute notation instead of dictionary notation:

```python
# Old (dictionary) syntax - NO LONGER WORKS
result = get_mail_template("welcome", params)
subject = result["subject"]
body = result["body"]

# New (object) syntax - CURRENT USAGE
result = get_mail_template("welcome", params)
subject = result.subject
body = result.body
html = result.html
name = result.name
```

The `MailTemplateParams` object has the following attributes:
- `name`: The name of the template
- `subject`: The rendered subject line
- `body`: The rendered plain text body
- `html`: The rendered HTML body

# Model Configuration Note

When using this library with multiple languages, ensure your `MailTemplate` model does not have `unique=True` on the `name` field, as this would prevent creating the same template name in different languages. The model should use `unique_together` for the `name` and `language` fields instead.