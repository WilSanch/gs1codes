from django.urls import path
from . import views

urlpatterns = [
    # ex: /polls/
    path('mark/', views.mark, name='mark_codes'),
    path('activate/', views.activate, name='prefix_activation'),
    path('pruebas/', views.pruebas, name='Pruebas'),
]