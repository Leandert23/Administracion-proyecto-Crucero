#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # cambio qlq
    # Ajuste: el proyecto real está dentro del subdirectorio
    # Administracion-proyecto-Crucero-Development-Almac-n/Administrador_Cruceros
    # Añadimos ese directorio al sys.path si no está
    base_dir = os.path.dirname(os.path.abspath(__file__))
    inner_proj = os.path.join(base_dir, 'Administracion-proyecto-Crucero-Development-Almac-n')
    if inner_proj not in sys.path:
        sys.path.insert(0, inner_proj)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Administrador_Cruceros.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
