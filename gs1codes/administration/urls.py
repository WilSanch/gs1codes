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
    path('inactivate/', views.inactivate, name='prefix_inactivation'),
    path('assignate/', views.assignate, name='prefix_assignation'),
    path('regroup/', views.regroup, name='prefix_regroup'),
    path('transfer/', views.transfer, name='prefix_transfer'),
    path('refund/', views.refund, name='prefix_refund'),
    path('update_validity_date/', views.update_validity_date, name='update_validity_date'),
    path('inactivate/', views.activate, name='prefix_inactivation'),
    path('RegistrarGTIN14/', views.RegistrarGTIN14, name='RegistrarGTIN14'),
    path('GetGtin14s/', views.GetGtin14s, name='GetGtin14s'),
    path('ListGetGtin14s/', views.ListGetGtin14s, name='ListGetGtin14s'),
    path('ListRegistrarGTIN14/', views.ListRegistrarGTIN14, name='ListRegistrarGTIN14'),
    # path('get_gpc/', views.get_gpc, name='get_gpc'),
    path("pt/", ptlist.as_view(), name="pt_list"),
    path("pt/<int:pk>/", ptdetail.as_view(), name="pt_detail"),
    # path("pt/", ptcreate.as_view(), name="pt_create"),
    path("GetCategoriesGPC/", GetCategoriesGPC.as_view(), name="GetCategoriesGPC"),
    path("GetMeasureUnits/", GetMeasureUnits.as_view(), name="GetMeasureUnits"),
    path('ejemplo/', views.ejemplo, name='ejemplo'),
    path('nit1/', views.nit1, name='nit1'),
    path('report/', views.report, name='report'),
    path('PowerBI/', views.reportPowerBI, name='PowerBI'),
    path('Cargue/', views.cargue, name='Cargue'),
    path('ProcesaBlobs/', views.procesaBlobs, name='ProcesaBlobs'),
    path('swagger-docs/', schema_view),
]