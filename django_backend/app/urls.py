from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('zusammenfassung/', views.summary, name='summary'),
    path('extra/<str:uuid>/', views.extra, name='extra')
] 