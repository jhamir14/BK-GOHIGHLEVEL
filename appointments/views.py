import requests
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Appointment
from .serializers import AppointmentSerializer
from django.conf import settings
from django.utils.dateparse import parse_datetime


@api_view(["POST"])
def create_appointment(request):
    payload = {
        "calendarId": settings.GHL_CALENDAR_ID,
        "locationId": settings.GHL_LOCATION_ID,
        "contactId": request.data.get("contactId", settings.GHL_CONTACT_ID),
        "startTime": request.data.get("startTime"),
        "endTime": request.data.get("endTime"),
        "title": request.data.get("title"),
        "description": request.data.get("description", ""),
    }

    headers = {
        "Authorization": f"Bearer {settings.GHL_API_KEY}",
        "Version": settings.GHL_VERSION,
        "Content-Type": "application/json",
    }

    url = f"{settings.GHL_API_BASE_URL}/calendars/events/appointments"
    r = requests.post(url, json=payload, headers=headers)

    if r.status_code == 201 or r.status_code == 200:
        appointment_data = r.json()

        # Usa "id" como appointmentId si no viene "appointmentId"
        appointment_id = appointment_data.get("appointmentId") or appointment_data.get("id")
        if not appointment_id:
            return Response({
                "message": "No se recibió appointmentId ni id del API externo"
            }, status=400)

        local_data = {
            "appointmentId": appointment_id,
            "calendarId": payload["calendarId"],
            "contactId": payload["contactId"],
            "locationId": payload.get("locationId"),
            "startTime": payload["startTime"],
            "endTime": payload["endTime"],
            "title": payload["title"],
            "description": payload["description"],
        }

        # 🔄 Si ya existe, actualiza la cita
        try:
            appointment = Appointment.objects.get(appointmentId=appointment_id)
            for field, value in local_data.items():
                setattr(appointment, field, value)
            appointment.save()
            return Response({
                "message": "Cita actualizada correctamente.",
                "data": appointment_data
            }, status=status.HTTP_200_OK)
        except Appointment.DoesNotExist:
            # Si no existe, crea una nueva
            serializer = AppointmentSerializer(data=local_data)
            if serializer.is_valid():
                serializer.save()
                return Response(appointment_data, status=status.HTTP_201_CREATED)
            else:
                print("❌ Errores al guardar en SQLite:", serializer.errors)
                return Response({
                    "message": "Error al guardar en SQLite",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

    return Response(r.json(), status=r.status_code)


@api_view(["GET"])
def list_appointments(request):
    """
    Lista citas desde GHL usando /calendars/events con filtros obligatorios.
    """
    # Lee fechas desde query params, ejemplo: ?start=2025-10-01&end=2025-10-05
    
    start = request.query_params.get("start")
    end = request.query_params.get("end")

    if not start or not end:
        return Response(
            {"error": "Debes enviar start y end en formato YYYY-MM-DD"},
            status=status.HTTP_400_BAD_REQUEST
        )

    from datetime import datetime, timezone
    try:
        # Convertir fechas a epoch millis
        start_date = datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        end_date = datetime.strptime(end, "%Y-%m-%d").replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
        start_millis = int(start_date.timestamp() * 1000)
        end_millis = int(end_date.timestamp() * 1000)
    except ValueError:
        return Response({"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}, status=400)

    params = {
        "locationId": settings.GHL_LOCATION_ID,
        "calendarId": settings.GHL_CALENDAR_ID,
        "startTime": start_millis,
        "endTime": end_millis
    }

    headers = {
        "Authorization": f"Bearer {settings.GHL_API_KEY}",
        "Version": settings.GHL_VERSION,
    }

    url = f"{settings.GHL_API_BASE_URL}/calendars/events"

    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        return Response(r.json(), status=status.HTTP_200_OK)

    return Response(r.json(), status=r.status_code)



@api_view(["GET"])
def list_local_appointments(request):
    """
    Muestra todas las citas guardadas localmente en SQLite.
    """
    appointments = Appointment.objects.all()
    serializer = AppointmentSerializer(appointments, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def sync_appointments(request):
    print("Sync endpoint hit!")  
    """
    Descarga citas desde GHL usando /calendars/events y las guarda en SQLite (sin duplicar).
    """
    headers = {
        "Authorization": f"Bearer {settings.GHL_API_KEY}",
        "Version": settings.GHL_VERSION,
    }
    url = f"{settings.GHL_API_BASE_URL}/calendars/events"
    params = {"calendarId": settings.GHL_CALENDAR_ID}

    r = requests.get(url, headers=headers, params=params)

    if r.status_code == 200:
        data = r.json()
        citas = data.get("appointments") or data.get("events") or []  # ajusta según la respuesta real
        nuevas = 0
        errores = []

        for cita in citas:
            # Asumiendo que cada 'cita' tiene id, calendarId, contactId, locationId, startTime, endTime, title, description
            appointment_id = cita.get("id")
            if appointment_id and not Appointment.objects.filter(appointmentId=appointment_id).exists():
                try:
                    Appointment.objects.create(
                        appointmentId=appointment_id,
                        calendarId=cita.get("calendarId"),
                        contactId=cita.get("contactId"),
                        locationId=cita.get("locationId"),
                        startTime=parse_datetime(cita.get("startTime")),
                        endTime=parse_datetime(cita.get("endTime")),
                        title=cita.get("title", ""),
                        description=cita.get("description", ""),
                    )
                    nuevas += 1
                except Exception as e:
                    errores.append(f"Error guardando cita {appointment_id}: {str(e)}")

        msg = f"Sincronización completa. {nuevas} citas nuevas guardadas."
        if errores:
            msg += " Algunos errores ocurrieron: " + "; ".join(errores)
        return Response({"message": msg})

    # Si falla la llamada a la API externa, devuelve el error
    return Response(r.json(), status=r.status_code)