from django.apps import AppConfig


class MailerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mailer"

    def ready(self):
        # Override Django's built-in send_mail
        from django.core import mail
        from .utils import send_mail as custom_send_mail
        mail.send_mail = custom_send_mail
