from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("title", "appointmentId", "calendarId", "contactId", "startTime", "endTime")
    list_filter = ("calendarId", "locationId", "startTime")
    search_fields = ("title", "appointmentId", "contactId", "description")
    ordering = ("-startTime",)
