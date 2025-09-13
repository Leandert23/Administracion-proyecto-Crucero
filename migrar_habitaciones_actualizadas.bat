@echo off
echo ============================================
echo MIGRACIONES - HABITACIONES ACTUALIZADAS
echo ============================================
echo.

cd /d "C:\Users\Roberto Siracusa\Desktop\proyectoSufrimiento\Administracion-proyecto-crucero"

echo Paso 1: Crear nuevas migraciones...
python manage.py makemigrations creador_embarcaciones
echo.

echo Paso 2: Aplicar todas las migraciones...
python manage.py migrate creador_embarcaciones
echo.

echo Paso 3: Verificar estado final...
python manage.py showmigrations creador_embarcaciones
echo.

echo ============================================
echo ¡MIGRACIONES COMPLETADAS!
echo ============================================
echo.
pause
