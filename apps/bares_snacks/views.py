from django.shortcuts import render
from django.shortcuts import HttpResponse

def bares_view(request):
  return render(request, 'bares_snacks/bares.html')
