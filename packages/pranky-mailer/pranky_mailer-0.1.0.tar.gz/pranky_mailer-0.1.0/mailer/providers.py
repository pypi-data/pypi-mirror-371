import boto3
import smtplib
from email.mime.text import MIMEText
from django.conf import settings


class SMTPProvider:
    def __init__(self, provider, sender):
        self.provider = provider
        self.sender = sender

    def send(self, subject, message, recipient_list):
        try:
            msg = MIMEText(message)
            msg['Subject'] = subject
            msg['From'] = self.sender.email
            msg['To'] = ", ".join(recipient_list)

            server = smtplib.SMTP(self.provider.host, self.provider.port)
            if self.provider.use_tls:
                server.starttls()
            server.login(self.provider.username, self.provider.password)
            server.sendmail(self.sender.email, recipient_list, msg.as_string())
            server.quit()
            return True, None
        except Exception as e:
            return False, str(e)


class SESProvider:
    def __init__(self, provider, sender):
        self.client = boto3.client(
            'ses',
            aws_access_key_id=provider.username,
            aws_secret_access_key=provider.password,
            region_name=getattr(settings, "AWS_REGION", "us-east-1")
        )
        self.sender = sender

    def send(self, subject, message, recipient_list):
        try:
            response = self.client.send_email(
                Source=self.sender.email,
                Destination={'ToAddresses': recipient_list},
                Message={
                    'Subject': {'Data': subject},
                    'Body': {'Text': {'Data': message}}
                }
            )
            return True, response
        except Exception as e:
            return False, str(e)
