from django.urls import path
from . import views

app_name = "notes"

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:user_pk>/send/", views.send, name="send"),
    path("<int:note_pk>/delete/", views.delete, name="delete"),
]