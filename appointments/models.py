from django.db import models

class Appointment(models.Model):
    appointmentId = models.CharField(max_length=255, unique=True)
    calendarId = models.CharField(max_length=255)
    contactId = models.CharField(max_length=255)
    locationId = models.CharField(max_length=255, null=True, blank=True)
    startTime = models.DateTimeField()
    endTime = models.DateTimeField()
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    
    # Agregar el campo status
    status = models.CharField(max_length=50, default="confirmed")  # Este es un campo opcional, con un valor por defecto

    def __str__(self):
        return f"{self.title} ({self.startTime} - {self.endTime})"
