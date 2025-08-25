from django.contrib import admin
from .models import MailTemplate


class MailTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "language", "subject", "created_at", "updated_at")
    search_fields = ("name", "subject")
    list_filter = ("name", "language", "created_at", "updated_at")


admin.site.register(MailTemplate, MailTemplateAdmin)
