from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_appointment, name="create_appointment"),
    path("list/", views.list_appointments, name="list_appointments"),
    path("sync/", views.sync_appointments, name="sync_appointments"),
    path("local/", views.list_local_appointments, name="list_local_appointments"),
]
