from pathlib import Path
from typing import List
import json

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.dateparse import parse_date

from ...Services.creacion_crucero_por_plantilla import crear_crucero_desde_plantilla
from ...models import Crucero

FIXTURES_DIR = Path(__file__).resolve().parents[3] / 'cruceros' / 'fixtures'
ARCHIVO_CRUCEROS = FIXTURES_DIR / 'cruceros_template.json'

class Command(BaseCommand):
    help = 'Crea cruceros desde fixture usando plantillas'

    def add_arguments(self, parser):
        parser.add_argument('--reiniciar', action='store_true', help='Elimina todos los cruceros antes de crear')
        parser.add_argument('--forzar', action='store_true', help='Recrea cruceros existentes')

    def handle(self, *args, **options):
        reiniciar = options['reiniciar']
        forzar = options['forzar']

        self.validar_archivo_fixture()
        datos = self.cargar_datos_fixture()

        if reiniciar:
            self.eliminar_cruceros_existentes()

        resumen = self.procesar_cruceros(datos, forzar)

        self.mostrar_resumen(resumen)

    def validar_archivo_fixture(self):
        if not ARCHIVO_CRUCEROS.exists():
            raise CommandError(f'Fixture no encontrado: {ARCHIVO_CRUCEROS}')

    def cargar_datos_fixture(self):
        try:
            with ARCHIVO_CRUCEROS.open(encoding='utf-8') as archivo:
                return json.load(archivo)
        except json.JSONDecodeError as error:
            raise CommandError(f'JSON inválido: {error}')

    def eliminar_cruceros_existentes(self):
        self.stdout.write('Eliminando cruceros existentes...')
        Crucero.objects.all().delete()

    def procesar_cruceros(self, datos, forzar):
        resumen = []
        
        with transaction.atomic():
            for entrada in datos:
                resultado = self.procesar_entrada_crucero(entrada, forzar)
                resumen.append(resultado)

        return resumen

    def procesar_entrada_crucero(self, entrada, forzar):
        tipo = entrada['tipo_crucero']
        codigo = entrada['codigo_identificacion']
        nombre = entrada['nombre']
        fecha_texto = entrada['fecha_botadura']
        descripcion = entrada.get('descripcion')

        fecha_botadura = parse_date(fecha_texto)
        
        if not fecha_botadura:
            return f'ERROR {codigo} fecha inválida: {fecha_texto}'

        crucero_existente = Crucero.objects.filter(codigo_identificacion=codigo).first()

        if crucero_existente:
            if forzar:
                crucero_existente.delete()
                self.stdout.write(f'Recreando {codigo} (eliminado)')
                creado_msg = self.crear_nuevo_crucero(tipo, codigo, nombre, fecha_botadura, descripcion)
                return creado_msg.replace('CREADO', 'RECREADO')
            else:
                return f'OMITIDO {codigo} ya existe'

        return self.crear_nuevo_crucero(tipo, codigo, nombre, fecha_botadura, descripcion)

    def crear_nuevo_crucero(self, tipo, codigo, nombre, fecha_botadura, descripcion):
        crucero = crear_crucero_desde_plantilla(
            tipo_crucero=tipo,
            codigo_identificacion=codigo,
            nombre=nombre,
            fecha_botadura=fecha_botadura,
            descripcion=descripcion,
        )
        return f'CREADO {crucero.codigo_identificacion} ({crucero.tipo_crucero})'

    def mostrar_resumen(self, resumen):
        for linea in resumen:
            self.stdout.write(linea)
        self.stdout.write(self.style.SUCCESS('Proceso finalizado.'))