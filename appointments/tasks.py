from datetime import datetime, timedelta, timezone
import requests
from django.conf import settings
from django.utils.timezone import make_aware, is_naive
from appointments.models import Appointment

def get_ghl_appointments_last_24h():
    
    # Citas - Ultimas 24H 
    now = datetime.utcnow().replace(microsecond=0)
    start = now - timedelta(days=1)         # para pruebas amplias

    # GHL espera startTime / endTime en milisegundos (según doc) :contentReference[oaicite:3]{index=3}
    start_ms = int(start.replace(tzinfo=timezone.utc).timestamp() * 1000)
    end_ms = int(now.replace(tzinfo=timezone.utc).timestamp() * 1000)

    # PARAMETROS DE GHL
    params = {
        "locationId": settings.GHL_LOCATION_ID,
        "startTime": start_ms,
        "endTime": end_ms,
        "calendarId": settings.GHL_CALENDAR_ID,
    }

    # ENCABEZADO DE GHL
    headers = {
        "Authorization": f"Bearer {settings.GHL_API_KEY}",
        "Version": settings.GHL_VERSION,
        "Accept": "application/json"
    }
    # API - GHL
    url = f"{settings.GHL_API_BASE_URL}/calendars/events"

    # devuelve en formato json
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        events = data.get("events", [])
        print("🔍 Request URL:", response.url)
        print("🔎 Status:", response.status_code)
        print("🔎 Response body:", response.text)
        print(f"✅ Citas obtenidas de GHL: {len(events)}")
        return events

    # maneja los errores 
    except requests.RequestException as e:
        print(f"❌ Error al obtener citas de GHL: {e}")
        if 'response' in locals():
            print("🔎 Respuesta:", response.status_code, response.text)
        return []



def compare_with_local(ghl_appointments):
    """
    Compara las citas obtenidas de GHL con las almacenadas localmente.
    - Crea las que faltan
    - Actualiza las modificadas
    - Detecta cancelaciones no reflejadas
    """
    print("🔍 Iniciando comparación de citas...")

    missing = []
    cancelled_not_reflected = []
    modified = []

    ghl_ids = {item['id'] for item in ghl_appointments}
    local_appointments = Appointment.objects.filter(appointmentId__in=ghl_ids)
    local_by_id = {a.appointmentId: a for a in local_appointments}

    for g in ghl_appointments:
        appointment_id = g['id']
        local = local_by_id.get(appointment_id)

        try:
            g_start = datetime.fromisoformat(g['startTime'].replace('Z', ''))
            g_time = make_aware(g_start, timezone.utc) if is_naive(g_start) else g_start
        except Exception as e:
            print(f"⚠️ Error al parsear startTime: {g['startTime']} - {e}")
            continue

        if not local:
            missing.append(g)
        else:
            differences = []

            # Comparar startTime
            local_time = make_aware(local.startTime, timezone.utc) if is_naive(local.startTime) else local.startTime
            if abs((g_time - local_time).total_seconds()) > 60:
                differences.append('startTime')

            # Comparar endTime
            try:
                g_end = datetime.fromisoformat(g['endTime'].replace('Z', ''))
                g_end_time = make_aware(g_end, timezone.utc) if is_naive(g_end) else g_end
                local_end_time = make_aware(local.endTime, timezone.utc) if is_naive(local.endTime) else local.endTime
                if abs((g_end_time - local_end_time).total_seconds()) > 60:
                    differences.append('endTime')
            except Exception as e:
                print(f"⚠️ Error al parsear endTime: {g.get('endTime')} - {e}")

            # Comparar título
            if g.get('title', '').strip() != (local.title or '').strip():
                differences.append('title')

            # Comparar descripción
            if g.get('description', '').strip() != (local.description or '').strip():
                differences.append('description')

            # Comparar estado
            ghl_status = g.get('appointmentStatus', '').lower()
            local_status = (local.status or '').lower()

            if ghl_status != local_status:
                differences.append('status')

            # 🔁 Detectar cancelaciones no reflejadas
            if ghl_status in ['cancelled', 'no-show'] and local_status not in ['cancelled', 'no-show']:
                cancelled_not_reflected.append((g, local))
                print(f"🚫 Cita cancelada en GHL pero no en local: {appointment_id} — actualizando estado...")
                local.status = ghl_status
                local.save()

            # 🔄 Si hay diferencias, actualizar campos locales
            if differences:
                modified.append((g, local, differences))
                print(f"✏️ Actualizando cita {appointment_id} - cambios: {differences}")
                local.title = g.get('title', local.title)
                local.description = g.get('description', local.description)
                local.status = ghl_status
                local.startTime = g_time

                if 'endTime' in g:
                    try:
                        local.endTime = g_end_time
                    except Exception as e:
                        print(f"⚠️ No se pudo actualizar endTime: {e}")

                local.save()

    print(f"📌 Faltantes en local: {len(missing)}")
    print(f"📌 Canceladas no reflejadas: {len(cancelled_not_reflected)}")
    print(f"📌 Citas modificadas: {len(modified)}")
    

"""
    # 🆕 Crear citas nuevas (faltantes)
    for g in missing:
        try:
            g_start = datetime.fromisoformat(g['startTime'].replace('Z', ''))
            g_end = datetime.fromisoformat(g['endTime'].replace('Z', ''))

            g_start_aware = make_aware(g_start.astimezone(timezone.utc).replace(tzinfo=None), timezone.utc)
            g_end_aware = make_aware(g_end.astimezone(timezone.utc).replace(tzinfo=None), timezone.utc)

            description = g.get('description', '')

            new_appointment = Appointment(
                appointmentId=g['id'],
                calendarId=g['calendarId'],
                contactId=g['contactId'],
                locationId=g['locationId'],
                startTime=g_start_aware,
                endTime=g_end_aware,
                title=g['title'],
                description=description,
                status=g.get('appointmentStatus', 'confirmed')
            )
            new_appointment.save()
            print(f"📝 Cita creada localmente: {new_appointment.title}")
        except Exception as e:
            print(f"⚠️ Error al crear cita: {e}")
"""
