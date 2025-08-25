import os
import sys
from setuptools import setup, find_packages

DESCRIPTION = "Manage email templates in DB with django"
VERSION = "0.1.2"
LONG_DESCRIPTION = None
try:
    LONG_DESCRIPTION = open("README.md").read()
except:
    pass

# プロジェクトの依存関係
install_requires = [
    "Django>=3.2",
]

# 開発・テスト用の依存関係
extras_require = {
    "dev": [
        "pytest",
        "pytest-django",
        "pytest-pythonpath",
        "tox",
        "factory_boy",
    ]
}

# python setup.py publish
if sys.argv[-1] == "publish":
    os.system("python setup.py sdist bdist_wheel")
    os.system("twine upload dist/*")
    sys.exit()

CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Framework :: Django",
]
setup(
    name="django_mail_model_template",
    version=VERSION,
    packages=find_packages(exclude=["tests*", "__pycache__", "*.pyc"]),
    include_package_data=True,
    author="Minoru Yokoo",
    author_email="yokoo@dreami.jp",
    url="https://github.com/dreamiyokoo/django-mail-model-template",
    license="MIT",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    platforms=["any"],
    classifiers=CLASSIFIERS,
    install_requires=install_requires,
    extras_require=extras_require,
)
