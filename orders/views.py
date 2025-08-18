from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

def order_list(request):
    return HttpResponse("Orders page")
