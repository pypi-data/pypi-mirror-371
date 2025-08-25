from django.conf import settings


DEFAULTS = {
    "APPOINTMENTS_PROVIDERS_MODEL": "auth.User",
    "APPOINTMENTS_RECIPIENTS_MODEL": "auth.User",
    "APPOINTMENTS_ACTIVITIES_MODEL": "simple_appointments.Activity",
    "APPOINTMENTS_STATUS_CHOICES": [
        ("", "Not specified"),
        ("pending", "Pending"),
        ("confirmed_by_recipients", "Confirmed by Recipients"),
        ("canceled_by_recipients", "Canceled by Recipients"),
        ("canceled_by_providers", "Canceled by Providers"),
        ("completed", "Completed"),
        ("no_show", "No-show"),
    ],
}


def get_setting(name):
    return getattr(settings, name, DEFAULTS[name])
