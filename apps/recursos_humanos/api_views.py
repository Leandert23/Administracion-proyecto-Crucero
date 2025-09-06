from rest_framework import generics
from .models import Personal
from .serializers import PersonalSerializer

class PersonalListCreateAPI(generics.ListCreateAPIView):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer

class PersonalRetrieveUpdateDeleteAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Personal.objects.all()
    serializer_class = PersonalSerializer
