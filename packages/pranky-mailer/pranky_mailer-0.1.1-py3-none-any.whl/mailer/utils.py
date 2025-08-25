from .services import send_mail_custom


def send_mail(subject, message, from_email, recipient_list, **kwargs):
    """
    Drop-in replacement for Django's send_mail.
    """
    provider = kwargs.get("provider", "smtp")  # default provider
    return send_mail_custom(subject, message, from_email, recipient_list, provider)
