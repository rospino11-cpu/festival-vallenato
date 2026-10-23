from django.contrib import admin
from .models import Usuario, Categoria, Candidato, Voto, ConfiguracionSitio, EventoProgramacion

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'cedula', 'first_name', 'email')
    search_fields = ('username', 'cedula', 'first_name')

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'estado', 'fecha_apertura', 'fecha_cierre')
    list_filter = ('estado',)

@admin.register(Candidato)
class CandidatoAdmin(admin.ModelAdmin):
    list_display = ('nombre_artistico', 'categoria')
    list_filter = ('categoria',)

@admin.register(Voto)
class VotoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'candidato', 'fecha')
    list_filter = ('candidato__categoria',)

@admin.register(ConfiguracionSitio)
class ConfiguracionSitioAdmin(admin.ModelAdmin):
    list_display = ('titulo_banner', 'subtitulo_banner')
    
    # Evita crear múltiples configuraciones para no saturar el panel
    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

@admin.register(EventoProgramacion)
class EventoProgramacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'edicion', 'lugar', 'fecha_inicio', 'fecha_fin')
    list_filter = ('edicion', 'fecha_inicio')
    search_fields = ('titulo', 'lugar')