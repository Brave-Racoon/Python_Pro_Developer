from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")


def home(request):
    return render(request, 'polls/home.html')
