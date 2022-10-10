from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView

from .models import Images

def index(request):
    return render(request, 'index.html')

        
 