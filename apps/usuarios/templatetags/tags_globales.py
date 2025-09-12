# usuarios/templatetags/auth_extras.py
from django import template
from django.urls import reverse, NoReverseMatch

register = template.Library()

@register.filter
def tiene_acceso_modulo(user, codigo_modulo):
    """Verifica si usuario tiene acceso a un módulo específico"""
    return user.tiene_acceso_modulo(codigo_modulo)

@register.filter
def puede_ver_modulo(user, codigo_modulo):
    """Alias para consistencia"""
    return user.tiene_acceso_modulo(codigo_modulo)

@register.simple_tag
def obtener_modulos_activos(user):
    """Retorna todos los módulos a los que tiene acceso"""
    return user.get_modulos_activos()

@register.inclusion_tag('partials/sidebar_item.html')
def render_sidebar_item(user, modulo):
    """Renderiza un item del sidebar si tiene acceso"""
    return {
        'tiene_acceso': user.tiene_acceso_modulo(modulo.codigo),
        'modulo': modulo,
        'es_superusuario': user.is_superuser
    }

@register.simple_tag(takes_context=True)
def es_url_activa(context, url_name):
    """Determina si la URL actual está activa"""
    request = context['request']
    try:
        current_url = reverse(url_name)
        return 'active' if request.path.startswith(current_url) else ''
    except NoReverseMatch:
        return ''