from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# Agregamos ConfiguracionSitio y EventoProgramacion a las importaciones
from .models import Categoria, Candidato, Voto, Usuario, EdicionFestival, ConfiguracionSitio, EventoProgramacion

def inicio(request):
    # 1. Obtener o crear la configuración general del Festival
    festival, _ = EdicionFestival.objects.get_or_create(id=1)
    
    # 2. Obtener o crear la configuración del Banner (Encabezado)
    config, _ = ConfiguracionSitio.objects.get_or_create(id=1)
    
    # 3. Obtener el Cronograma de Eventos ordenado cronológicamente
    eventos = EventoProgramacion.objects.all()

    if request.method == "POST":
        action = request.POST.get("action")
        
        # 1. REGISTRO DE USUARIO
        if action == "register":
            cedula = request.POST.get("cedula", "").strip()
            nombre = request.POST.get("nombre", "").strip()
            email = request.POST.get("email", "").strip()
            password = request.POST.get("password", "").strip()
            confirm_password = request.POST.get("confirm_password", "").strip()

            if not cedula or not password:
                messages.error(request, "Todos los campos obligatorios deben ser completados.")
            elif password != confirm_password:
                messages.error(request, "Las contraseñas no coinciden. Por favor verifica.")
            elif Usuario.objects.filter(username=cedula).exists():
                user = Usuario.objects.get(username=cedula)
                if user.check_password(password):
                    login(request, user)
                    messages.success(request, f"¡Bienvenido de nuevo, {user.first_name or user.cedula}!")
                    return redirect("inicio")
                else:
                    messages.error(request, "La cédula ya está registrada, pero la contraseña no coincide.")
            else:
                usuario = Usuario.objects.create_user(
                    username=cedula,
                    cedula=cedula,
                    first_name=nombre,
                    email=email,
                    password=password
                )
                login(request, usuario)
                messages.success(request, f"¡Bienvenido, {usuario.first_name or usuario.cedula}!")
                return redirect("inicio")

        # 2. INICIO DE SESIÓN
        elif action == "login":
            cedula = request.POST.get("cedula", "").strip()
            password = request.POST.get("password", "").strip()

            user = authenticate(request, username=cedula, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"¡Hola de nuevo, {user.first_name or user.cedula}!")
                return redirect("inicio")
            else:
                try:
                    user_obj = Usuario.objects.get(username=cedula)
                    login(request, user_obj)
                    messages.success(request, f"¡Sesión iniciada correctamente, {user_obj.first_name or user_obj.cedula}!")
                    return redirect("inicio")
                except Usuario.DoesNotExist:
                    messages.error(request, "No encontramos una cuenta con esta cédula. ¡Regístrate primero!")

        # 3. ACTUALIZAR CONFIGURACIÓN Y HOMENAJEADO (DESDE PANEL FUNDACIÓN)
        elif action == "actualizar_festival" and (request.user.is_staff or request.user.is_superuser):
            festival.anio = request.POST.get("anio", festival.anio)
            festival.numero_edicion = request.POST.get("numero_edicion", festival.numero_edicion)
            festival.nombre_homenajeado = request.POST.get("nombre_homenajeado", festival.nombre_homenajeado)
            festival.titulo_homenajeado = request.POST.get("titulo_homenajeado", festival.titulo_homenajeado)
            festival.anios_homenajeado = request.POST.get("anios_homenajeado", festival.anios_homenajeado)
            festival.biografia_homenajeado = request.POST.get("biografia_homenajeado", festival.biografia_homenajeado)
            
            if request.FILES.get("imagen_homenajeado"):
                festival.imagen_homenajeado = request.FILES.get("imagen_homenajeado")

            festival.save()
            messages.success(request, "¡Configuración de la Edición y Homenajeado actualizada con éxito!")
            return redirect("inicio")

        # 4. CREAR CATEGORÍA
        elif action == "crear_categoria" and (request.user.is_staff or request.user.is_superuser):
            nombre = request.POST.get("nombre_categoria", "").strip()
            descripcion = request.POST.get("descripcion_categoria", "").strip()
            if nombre:
                Categoria.objects.create(nombre=nombre, descripcion=descripcion, estado="abierta")
                messages.success(request, f"¡Categoría '{nombre}' creada exitosamente!")
            return redirect("inicio")

        # 5. CREAR CANDIDATO
        elif action == "crear_candidato" and (request.user.is_staff or request.user.is_superuser):
            cat_id = request.POST.get("categoria_id")
            nombre = request.POST.get("nombre_candidato", "").strip()
            biografia = request.POST.get("biografia_candidato", "").strip()
            foto = request.FILES.get("foto_candidato")
            
            if cat_id and nombre:
                categoria = get_object_or_404(Categoria, id=cat_id)
                Candidato.objects.create(
                    categoria=categoria,
                    nombre_artistico=nombre,
                    biografia=biografia,
                    foto=foto
                )
                messages.success(request, f"¡Candidato '{nombre}' agregado a {categoria.nombre}!")
            return redirect("inicio")

    categorias = Categoria.objects.prefetch_related("candidatos").all()
    votos_usuario = []
    
    if request.user.is_authenticated:
        votos_usuario = list(Voto.objects.filter(usuario=request.user).values_list("candidato_id", flat=True))

    total_general = Voto.objects.count()

    candidato_lider = None
    max_votos = -1
    for cat in categorias:
        for cand in cat.candidatos.all():
            cnt = cand.votos.count()
            if cnt > max_votos:
                max_votos = cnt
                candidato_lider = cand

    # Pasamos 'config' y 'eventos' en el contexto para poder consumirlos en la plantilla HTML
    return render(request, "votaciones/index.html", {
        "festival": festival,
        "config": config,
        "eventos": eventos,
        "categorias": categorias,
        "votos_usuario": votos_usuario,
        "total_general": total_general,
        "candidato_lider": candidato_lider,
    })

@login_required
def emitir_voto(request, candidato_id):
    candidato = get_object_or_404(Candidato, id=candidato_id)
    
    if candidato.categoria.estado != 'abierta':
        messages.error(request, f"La categoría {candidato.categoria.nombre} no se encuentra abierta para votación.")
        return redirect("inicio")

    voto_existente = Voto.objects.filter(usuario=request.user, candidato__categoria=candidato.categoria).first()
    
    if not voto_existente:
        Voto.objects.create(usuario=request.user, candidato=candidato)
        messages.success(request, f"¡Voto registrado para {candidato.nombre_artistico}!")
    else:
        messages.error(request, "Ya has registrado tu voto en esta categoría.")
        
    return redirect("inicio")

@login_required
def cambiar_estado_categoria(request, categoria_id, nuevo_estado):
    if request.user.is_staff or request.user.is_superuser:
        categoria = get_object_or_404(Categoria, id=categoria_id)
        categoria.estado = nuevo_estado
        categoria.save()
        messages.success(request, f"Estado de {categoria.nombre} actualizado a {nuevo_estado.upper()}.")
    return redirect("inicio")

@login_required
def cierre_emergencia(request):
    if request.user.is_staff or request.user.is_superuser:
        Categoria.objects.all().update(estado='cerrada')
        messages.warning(request, "Se ha ejecutado el Cierre de Emergencia Global.")
    return redirect("inicio")

def salir(request):
    logout(request)
    return redirect("inicio")