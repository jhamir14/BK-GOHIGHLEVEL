# BK-GOHIGHLEVEL

---

### Reconciliación de Citas GHL con Django

### 1. 📂 Estructura guia del proyecto

Se utilizan tres archivos clave para ejecutar la sincronización de citas:

-appointments/tasks.py: funciones para obtener y comparar citas con GHL.

-appointments/management/commands/reconcile_appointments.py: comando personalizado que ejecuta la reconciliación.

-config/settings.py: configuración del proyecto, lectura del archivo .env.

-También es necesario tener un archivo .env con las variables necesarias.

---

### 2. ⚙️ Configuración del entorno

Crea un archivo llamado .env en la raíz del proyecto con las siguientes variables:

SECRET_KEY=tu_clave_django
DEBUG=True

GHL_API_BASE_URL=https://api.gohighlevel.com/v1
GHL_API_KEY=tu_token_ghl
GHL_CALENDAR_ID=calendar_id_a_usar
GHL_LOCATION_ID=location_id
GHL_CONTACT_ID=contact_id


Estas variables serán leídas desde settings.py.

---

### 3. 🧪 ¿Qué hace el comando?

Cuando ejecutas:

python manage.py reconcile_appointments


-El sistema:

  Convierte fechas locales a formato UTC "aware".
  
  Obtiene citas de las últimas 24 horas desde GHL.
  
  Compara con las citas locales:
  
  Si hay diferencias → actualiza.
  
  Si falta una cita local → la detecta (y se puede crear si se activa ese bloque).
  
  Si fue cancelada en GHL pero sigue activa localmente → se actualiza el estado.

-Muestra en consola un resumen:

  🚀 Iniciando reconciliación de citas...
  
  ✅ Citas obtenidas de GHL: 12
  
  ✏️ Actualizando cita abc123 - cambios: ['title', 'status']
  
  🚫 Cita cancelada en GHL pero no en local: xyz456 — actualizando estado...
  
  📌 Faltantes en local: 3
  
  📌 Canceladas no reflejadas: 2
  
  📌 Citas modificadas: 5
  
  ✅ Reconciliación finalizada.
  
---

### 4. 🗓️ Automatizar con Programador de tareas (Windows)

Puedes ejecutar este comando automáticamente todos los días:

Abre el Programador de tareas de Windows.

Crea una nueva tarea básica.

  -Nombre de la tarea, luego siguiente.
  
  -Desencadenar, establecer el formato de iniciación (diario, semanalmente, etc) y la fecha de inicio y su hora de inico.
  
  -En el paso "Acción", selecciona Iniciar un programa.

Completa con:

  Programa/script:
  
  C:\ruta\a\tu\venv\Scripts\python.exe    o    la ruta de tu proyecto y luego incluir (venv\Scripts\python.exe)


Argumentos:

  manage.py reconcile_appointments


Iniciar en:

  D:\ruta\del\proyecto\   o    la ruta de tu proyecto


Establece la hora diaria deseada en "Desencadenadores".

---

### 5. ✅ Requisitos previos

Python

Django instalado y configurado

Entorno virtual activo

  #crear
  -python -m venv venv
  #activar
  -venv\Scripts\Activate

Proyecto Django funcional con la app appointments

Instalacion 

  -pip install -r requirements.txt
  
  -python manage.py migrate

---

### 6. 💡 Mejoras sugeridas

  -Activar la creación automática de citas nuevas (bloque actualmente comentado).
  
  -Agregar logs persistentes (archivos .log).
  
  -Agregar pruebas automatizadas unitarias.
  
  -Configurar notificaciones por correo en caso de errores.

---

### 7. 🔚 Conclusión

  Este sistema automatiza y asegura la integridad de las citas entre GHL y tu base de datos local. La ejecución diaria 
  garantiza que siempre estén sincronizadas las últimas 24 horas de actividad.

---
