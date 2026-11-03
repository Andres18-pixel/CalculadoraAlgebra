from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('api/calcular/', views.calcular_api, name='calcular_api'),
]