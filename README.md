# BK-GOHIGHLEVEL

## 📌 Descripción
Este proyecto implementa un **backend en Django** que permite la integración con la API de **GoHighLevel (LeadConnectorHQ)** para la gestión de citas en un calendario.  

Se creó un flujo para:  
- Conectarse a la API de GoHighLevel.  
- Crear citas desde un endpoint local (`/api/appointments/create/`).  
- Consultar citas en GoHighLevel usando la API oficial.  
- Guardar el `appointmentId` también de forma local en SQLite.  
- Configuración segura mediante variables de entorno (`.env`).  
- Implementar **paginación local**, ya que el endpoint de GHL no trae `nextPageToken`.  

---

## ⚙️ Instalación y Configuración

### 1. Clonar el repositorio

git clone https://github.com/usuario/BK-GOHIGHLEVEL.git
cd BK-GOHIGHLEVEL

### 2. Crear entorno virtual

python -m venv venv

En Windows:
venv\Scripts\activate

En Linux/Mac:
source venv/bin/activate

### 3. Instalar dependencias

pip install -r requirements.txt

### 4. Crear archivo .env

En la raíz del proyecto, crear un archivo llamado .env con este contenido (reemplazar valores con los tuyos de GoHighLevel):

SECRET_KEY=tu_clave_django
DEBUG=True
GHL_API_BASE_URL=https://services.leadconnectorhq.com
GHL_API_KEY=tu_api_key
GHL_CALENDAR_ID=tu_calendar_id
GHL_LOCATION_ID=tu_location_id
GHL_CONTACT_ID=tu_contact_id

### 5. Migrar la base de datos

python manage.py migrate

### 6. Ejecutar el servidor local

python manage.py runserver
👉 Servidor disponible en:
http://127.0.0.1:8000/

🚀 Endpoints Implementados

### 7. Crear cita (POST)

http://127.0.0.1:8000/api/appointments/create/

Ejemplo de body en JSON:

json
Copiar código
{
  "calendarId": "tu_calendar_id",
  "contactId": "tu_contact_id",
  "locationId": "tu_location_id",
  "startTime": "2025-10-02T15:00:00Z",
  "endTime": "2025-10-02T15:30:00Z",
  "title": "Consulta de prueba"
}

### 8. Consultar citas en GHL (GET)
http://127.0.0.1:8000/api/appointments/list/?start=2025-10-01&end=2025-10-05&limit=3&page=1

start y end → Obligatorios (rango de fechas en formato YYYY-MM-DD).

limit → Opcional (cuántas citas por página, por defecto 3).

page → Opcional (número de página, por defecto 1).

📌 Nota importante sobre paginación:
El endpoint de GHL (/calendars/events) no devuelve nextPageToken, solo todos los eventos del rango de fechas.
Por eso se implementó una paginación manual en el backend usando limit y page.

Ejemplo de respuesta:

{
  "events": [
    { "id": "cita1", "title": "Consulta inicial", "startTime": "2025-10-01T15:00:00Z" },
    { "id": "cita2", "title": "Seguimiento", "startTime": "2025-10-02T10:00:00Z" }
  ],
  "page": 1,
  "limit": 2,
  "total": 5,
  "has_next": true
}

### 9. Ver citas locales (SQLite)
http://127.0.0.1:8000/api/appointments/local/

Devuelve todas las citas almacenadas en la base local SQLite.

📌 Nota importante
tambien se puede desde la shell ejecutando:

python manage.py shell                

y agregando:

for a in Appointment.objects.order_by("startTime").values():
    for key, value in a.items():
        print(f"{key}: {value}")
    print("-" * 40)

o tambien:

from appointments.models import Appointment
print(Appointment.objects.all())

no podras ver nada si antes no creas una cita desde postman.

✅ Resultados

Se probó con Postman y la creación de citas funcionó correctamente.

Las citas creadas se visualizaron en el dashboard de GoHighLevel (ReflexoPerú).

La consulta de citas devolvió los resultados correctamente con rango de fechas.

Se implementó paginación local porque el endpoint no trae nextPageToken.

Las citas creadas también se almacenaron en la base local SQLite para control interno.

📄 Notas
### 10. Recomendaciones

No olvides actualizar requirements.txt después de instalar paquetes:

pip freeze > requirements.txt

Este proyecto está en entorno de desarrollo local. Para producción se recomienda usar un servidor WSGI/ASGI como Gunicorn o Uvicorn.

Si quieres ver tus citas locales en SQLite, usa:


📦 requirements.txt
txt
Copiar código
asgiref==3.9.2
certifi==2025.8.3
charset-normalizer==3.4.3
Django==5.2.6
djangorestframework==3.16.1
idna==3.10
requests==2.32.5
sqlparse==0.5.3
tzdata==2025.2
urllib3==2.5.0

### 11. archivos a incluir en .gitignore

# ignorar el entorno virtual
venv/

# Archivos de Python compilados
__pycache__/
*.pyc
*.pyo
*.pyd

# archivos de entorno
.env
*.env

# base de datos
*.sqlite3
