from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView

from .models import Images

def index(request):
    if request.user.is_superuser:
        img = Images.objects.all()
        context = {
            'img':img
        }
        return render(request, 'server.html', context)
    
    else:
        return render(request, 'client.html')

        
