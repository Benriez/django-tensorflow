from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView

def index(request):
    return HttpResponseRedirect('/admin/app/images') 
