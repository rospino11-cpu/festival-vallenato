from django.urls import path
from . import views

urlpatterns = [
    path("", views.inicio, name="inicio"),
    path("votar/<int:candidato_id>/", views.emitir_voto, name="emitir_voto"),
    path("admin-panel/estado/<int:categoria_id>/<str:nuevo_estado>/", views.cambiar_estado_categoria, name="cambiar_estado_categoria"),
    path("admin-panel/cierre-emergencia/", views.cierre_emergencia, name="cierre_emergencia"),
    path("salir/", views.salir, name="salir"),
]