from rest_framework import serializers
from .models import Personal, Amonestacion

class AmonestacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Amonestacion
        fields = ['estado', 'detalle']

class PersonalSerializer(serializers.ModelSerializer):
    nombre = serializers.CharField(read_only=True)
    apellido = serializers.CharField(read_only=True)
    amonestacion = AmonestacionSerializer(required=False)

    class Meta:
        model = Personal
        fields = ['id', 'nombre', 'apellido', 'salario', 'edad', 'anios_experiencia',
                  'categoria', 'puesto', 'pStatus', 'amonestacion']


    def update(self, instance, validated_data):
        amonestacion_data = validated_data.pop('amonestacion', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if amonestacion_data is not None:
            Amonestacion.objects.update_or_create(
                personal=instance,
                defaults=amonestacion_data
            )
        return instance
