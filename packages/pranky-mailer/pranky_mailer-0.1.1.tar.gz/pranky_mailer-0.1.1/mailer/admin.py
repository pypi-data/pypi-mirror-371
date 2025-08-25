from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
from django.db.models.functions import TruncDate, TruncMonth

from .models import MailProvider, SenderEmail, MailLog


# Register models normally
admin.site.register(MailProvider)
admin.site.register(SenderEmail)
admin.site.register(MailLog)


# Add custom dashboard view
def mailer_dashboard(request):
    today = timezone.now().date()
    month_start = today.replace(day=1)

    # Daily chart (for current month)
    daily_logs = (
        MailLog.objects.filter(sent_at__gte=month_start)
        .annotate(day=TruncDate("sent_at"))
        .values("day")
        .annotate(total=Count("id"))
        .order_by("day")
    )

    # Monthly chart (all time)
    monthly_logs = (
        MailLog.objects.all()
        .annotate(month=TruncMonth("sent_at"))
        .values("month")
        .annotate(total=Count("id"))
        .order_by("month")
    )

    # Provider quota status
    providers = []
    for provider in MailProvider.objects.filter(active=True):
        daily_count = MailLog.objects.filter(provider=provider, sent_at__date=today).count()
        monthly_count = MailLog.objects.filter(provider=provider, sent_at__gte=month_start).count()
        providers.append({
            "name": provider.get_name_display(),
            "daily_count": daily_count,
            "daily_limit": provider.daily_limit,
            "monthly_count": monthly_count,
            "monthly_limit": provider.monthly_limit,
        })

    context = {
        "title": "Mailer Dashboard",
        "daily_logs": list(daily_logs),
        "monthly_logs": list(monthly_logs),
        "providers": providers,
    }
    return render(request, "admin/mailer_dashboard.html", context)


# Add URL under admin
class MailerAdminSite(admin.AdminSite):
    site_header = "Mailer Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(mailer_dashboard), name="mailer-dashboard"),
        ]
        return custom_urls + urls


# Replace default admin site with our custom one
admin.site.__class__ = MailerAdminSite
