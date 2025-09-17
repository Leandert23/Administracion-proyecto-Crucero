@csrf_exempt
@require_GET
def listar_usuarios_custom(request):
    usuarios = []
    for u in UsuarioCustom.objects.select_related('rol').all():
        usuarios.append({
            'id': u.id,
            'username': u.username,
            'nombre': u.nombre,
            'apellido': u.apellido,
            'rol_nombre': u.rol.nombre if u.rol else ''
        })
    return JsonResponse({'ok': True, 'usuarios': usuarios})
