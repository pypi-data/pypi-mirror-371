from django.utils import timezone
from .models import MailLog, MailProvider, SenderEmail
from .providers import SMTPProvider, SESProvider


def get_provider_instance(provider, sender):
    if provider.name == "smtp":
        return SMTPProvider(provider, sender)
    elif provider.name == "ses":
        return SESProvider(provider, sender)
    else:
        raise ValueError("Unknown provider")


def check_limits(provider):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    daily_count = MailLog.objects.filter(provider=provider, sent_at__date=today).count()
    monthly_count = MailLog.objects.filter(provider=provider, sent_at__gte=month_start).count()

    if daily_count >= provider.daily_limit:
        return False, "Daily limit reached"
    if monthly_count >= provider.monthly_limit:
        return False, "Monthly limit reached"

    return True, None


def send_mail_custom(subject, message, from_email, recipient_list, provider_name="smtp"):
    try:
        provider = MailProvider.objects.get(name=provider_name, active=True)
        sender = SenderEmail.objects.filter(provider=provider, email=from_email, verified=True).first()

        if not sender:
            raise ValueError("Sender email not verified or not found")

        can_send, reason = check_limits(provider)
        if not can_send:
            raise ValueError(reason)

        provider_instance = get_provider_instance(provider, sender)
        success, response = provider_instance.send(subject, message, recipient_list)

        MailLog.objects.create(
            provider=provider,
            sender=sender,
            to=", ".join(recipient_list),
            subject=subject,
            body=message,
            status="success" if success else "failed",
            error_message=None if success else str(response),
        )
        return success
    except Exception as e:
        MailLog.objects.create(
            provider=None,
            sender=None,
            to=", ".join(recipient_list),
            subject=subject,
            body=message,
            status="failed",
            error_message=str(e),
        )
        return False
