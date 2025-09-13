from django.db.models import Sum
from .models import Personal

"""
Funciones y variables exportables para otros módulos:
- get_personal_counts(): retorna dict con conteos por estado
- get_total_salarios(): retorna suma de salarios
- get_personal_por_categoria(categoria): queryset filtrado por categoria
"""

def get_personal_counts():
    return {
        'activo': Personal.objects.filter(pStatus=1).count(),
        'inactivo': Personal.objects.filter(pStatus=2).count(),
        'de_baja': Personal.objects.filter(pStatus=3).count(),
    }


def get_total_amonestados():
    # Ahora las amonestaciones están unificadas dentro de Personal
    return Personal.objects.filter(amon_estado=True).count()


def get_total_salarios():
    return Personal.objects.aggregate(total=Sum('salario'))['total'] or 0


def get_personal_por_categoria(categoria):
    return Personal.objects.filter(categoria=categoria)
