#appointments/management/commands/reconcile_appointments.py

import os
from django.core.management.base import BaseCommand
from appointments.tasks import get_ghl_appointments_last_24h, compare_with_local
from django.utils.timezone import make_aware
from appointments.models import Appointment
from datetime import datetime, timezone

class Command(BaseCommand):
    help = 'Reconciliación diaria de citas con GHL (últimas 24 horas)'

    def handle(self, *args, **kwargs):
        # Asegurar de que todas las fechas locales estén "aware" y en UTC
        appointments = Appointment.objects.all()
        for appointment in appointments:
            if appointment.startTime.tzinfo is None:  # Si la fecha no tiene zona horaria
                appointment.startTime = make_aware(appointment.startTime, timezone.utc)  # Convertir a UTC
                appointment.endTime = make_aware(appointment.endTime, timezone.utc)  # Convertir a UTC
                appointment.save()

        self.stdout.write("🚀 Iniciando reconciliación de citas...")

        # Obtener citas de GHL
        appointments = get_ghl_appointments_last_24h()
        self.stdout.write(self.style.SUCCESS(f"✅ Citas obtenidas de GHL: {len(appointments)}"))
        
        # Comparar las citas obtenidas de GHL con las locales
        compare_with_local(appointments)

        self.stdout.write(self.style.SUCCESS("✅ Reconciliación finalizada."))
