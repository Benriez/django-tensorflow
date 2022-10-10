from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView

from .models import Images

def index(request):
    if "next" in request.POST:
        return render(request, 'summary.html')

    return render(request, 'index.html')

  
 