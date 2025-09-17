from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def add_class(field, css_class):
    """
    Agrega una clase CSS a un campo de formulario de Django
    """
    if hasattr(field, 'as_widget'):
        # Es un campo de formulario de Django
        return field.as_widget(attrs={'class': css_class})
    else:
        # Si no es un campo de formulario, devolver tal cual
        return field