from django.urls import path
from . import views

urlpatterns = [
    # ex: /polls/
    path('mark/', views.mark, name='mark_codes')
]