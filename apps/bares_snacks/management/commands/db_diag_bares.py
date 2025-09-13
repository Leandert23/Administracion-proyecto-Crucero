from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection
from apps.bares_snacks.models import ProductoBar

class Command(BaseCommand):
    help = "Diagnose DB path, applied migrations, DetallePedido columns, and ProductoBar count."

    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        self.stdout.write(f"DB path: {db_path}")
        with connection.cursor() as cursor:
            cursor.execute("SELECT app, name, applied FROM django_migrations WHERE app='bares_snacks' ORDER BY name")
            migs = cursor.fetchall()
            self.stdout.write("Applied migrations for bares_snacks:")
            
            for row in migs:
                self.stdout.write(f"  - {row[1]} @ {row[2]}")

            cursor.execute("PRAGMA table_info('bares_snacks_detallepedido')")
            cols = cursor.fetchall()
            self.stdout.write("bares_snacks_detallepedido columns:")
            for c in cols:
                self.stdout.write(f"  - {c[1]} ({c[2]})")

        cnt = ProductoBar.objects.count()
        self.stdout.write(f"ProductoBar count: {cnt}")
