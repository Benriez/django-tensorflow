from django.shortcuts import HttpResponse, HttpResponseRedirect
from django.views.generic import TemplateView

def index(request):
    return HttpResponseRedirect('/admin/app/order') 


class CRMView(TemplateView):
    template_name = "admin/crm.html"

class KommunikationstoolView(TemplateView):
    template_name = "admin/kommunikationstool.html"

class WarenwirtschaftssystemView(TemplateView):
    template_name = "admin/warenwirtschaftssystem.html"