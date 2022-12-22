import pandas as pd
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse

# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect('/login')

