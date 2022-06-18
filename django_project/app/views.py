from django.shortcuts import render
from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView


def index(request):
    if request.user.is_superuser:
        return HttpResponse('server view')
        #return HttpResponseRedirect('/admin/app/images') 
    
    else:

        return render(request, 'client.html')
