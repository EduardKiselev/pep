from django.shortcuts import render
from calc.models import Food

def index(request):
    template = 'calc/calc.html'
    results = Food.objects.all

    return render(request, template, {"showcity": results})
