from rest_framework import serializers
from .models import Appointment
from django.utils import timezone

class AppointmentSerializer(serializers.ModelSerializer):
    
    startTime = serializers.DateTimeField()
    endTime = serializers.DateTimeField()
    
    
    class Meta:
        model = Appointment
        fields = "__all__"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Convierte los datetimes que vienen en UTC a la zona local antes de devolverlos
        start = instance.startTime
        end = instance.endTime
        # `timezone.localtime(...)` convierte el datetime aware (UTC) a la zona activa
        ret['startTime'] = timezone.localtime(start).isoformat()
        ret['endTime'] = timezone.localtime(end).isoformat()
        return ret
