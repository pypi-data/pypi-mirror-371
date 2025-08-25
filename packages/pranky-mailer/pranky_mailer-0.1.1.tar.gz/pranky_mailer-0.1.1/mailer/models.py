from django.utils import timezone
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import admin
from django.db import models


# Dummy model to add dashboard link in sidebar
class MailerDashboard(models.Model):
    class Meta:
        managed = False
        verbose_name = "📊 Mailer Dashboard"
        verbose_name_plural = "📊 Mailer Dashboard"


@admin.register(MailerDashboard)
class MailerDashboardAdmin(admin.ModelAdmin):
    def changelist_view(self, request, extra_context=None):
        # Redirect straight to dashboard
        return HttpResponseRedirect(reverse("admin:mailer-dashboard"))

class MailProvider(models.Model):
    PROVIDER_CHOICES = [
        ("smtp", "SMTP"),
        ("ses", "AWS SES"),
    ]

    name = models.CharField(max_length=50, choices=PROVIDER_CHOICES)
    host = models.CharField(max_length=255, blank=True, null=True)  # for SMTP
    port = models.IntegerField(blank=True, null=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255, blank=True, null=True)
    use_tls = models.BooleanField(default=True)

    daily_limit = models.IntegerField(default=500)
    monthly_limit = models.IntegerField(default=5000)

    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_name_display()}"


class SenderEmail(models.Model):
    provider = models.ForeignKey(MailProvider, on_delete=models.CASCADE, related_name="senders")
    email = models.EmailField()
    verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} ({self.provider.name})"


class MailLog(models.Model):
    provider = models.ForeignKey(MailProvider, on_delete=models.SET_NULL, null=True)
    sender = models.ForeignKey(SenderEmail, on_delete=models.SET_NULL, null=True, blank=True)
    to = models.TextField()
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=20, choices=[("success", "Success"), ("failed", "Failed")])
    error_message = models.TextField(blank=True, null=True)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.subject} → {self.to} ({self.status})"


