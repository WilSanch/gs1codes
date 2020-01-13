from django.urls import path
from . import views 
from administration.views.core import ptlist,GetCategoriesGPC,ptdetail,GetMeasureUnits
from rest_framework_swagger.views import get_swagger_view
from django.views.generic import TemplateView

schema_view = get_swagger_view(title='API Codes GS1')

urlpatterns = [
    # ex: /polls/
    path('mark/', views.mark, name='mark_codes'),
    path('activate/', views.activate, name='prefix_activation'),
    path('pruebas/', views.pruebas, name='Pruebas'),
    # path('get_gpc/', views.get_gpc, name='get_gpc'),
    path("pt/", ptlist.as_view(), name="pt_list"),
    path("pt/<int:pk>/", ptdetail.as_view(), name="pt_detail"),
    # path("pt/", ptcreate.as_view(), name="pt_create"),
    path("GetCategoriesGPC/", GetCategoriesGPC.as_view(), name="GetCategoriesGPC"),
    path("GetMeasureUnits/", GetMeasureUnits.as_view(), name="GetMeasureUnits"),
    path('swagger-docs/', schema_view),
]