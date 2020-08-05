from django.urls import path
from . import views 
from administration.views.core import ptlist,GetCategoriesGPC,ptdetail,GetMeasureUnits
from administration.views.prefix import load_enterprise
from rest_framework_swagger.views import get_swagger_view
from django.views.generic import TemplateView
from django.conf.urls import url

schema_view = get_swagger_view(title='API Codes GS1')

urlpatterns = [
    # ex: /polls/
    path('mark/', views.mark, name='mark_codes'),
    path('activate/', views.activate, name='prefix_activation'),
    path('inactivate/', views.activate, name='prefix_inactivation'),
    path('inactivate/', views.inactivate, name='prefix_inactivation'),
    path('assignate/', views.assignate, name='prefix_assignation'),
    url(r'^assignate_search_enterprise/$', views.assignate_search_enterprise, name='assignate_search_enterprise'),
    path('assignation/', views.assignation, name='assignation'),
    path('get/ajax/validate/nit', load_enterprise, name = "validate_nit"),
    path('ajax/load/codetypes/', views.load_code_types, name='ajax_load_codetypes'), 
    path('ajax/load/prefixtypes/', views.load_prefix_types, name='ajax_load_prefixtypes'), 
    path('ajax/load/codestable/', views.load_codes_table, name='ajax_load_codestable'), 
    path('ajax/load/prefixtable/<opc>/', views.load_prefix_table, name='ajax_load_prefixtable'), 
    path('ajax/load/btn2ndgrid/', views.function_2nd_grid, name='ajax_function_2nd_grid'),
    path('transfer_prefix/', views.transfer_prefix, name='transfer_prefix'),    
    path('update_validity_date_prefix/', views.update_validity_date_prefix, name='update_validity_date_prefix'),    
    url(r'^action_prefix/(?P<enterprise_nit>[-a-zA-Z0-9_]+)/(?P<opc>\d+)/$', views.action_prefix, name='action_prefix'),
    path('regroup/', views.regroup, name='prefix_regroup'),
    path('transfer/', views.transfer, name='prefix_transfer'),
    path('refund/', views.refund, name='prefix_refund'),
    path('update_validity_date/', views.update_validity_date, name='update_validity_date'),
    path('inactivate/', views.activate, name='prefix_inactivation'),
    path('enterprise_modify/<enterprise>/', views.enterprise_modify, name='enterprise_modify'),
    path('RegistrarGTIN14/', views.RegistrarGTIN14, name='RegistrarGTIN14'),
    path('GetGtin14s/', views.GetGtin14s, name='GetGtin14s'),
    path('ListGetGtin14s/', views.ListGetGtin14s, name='ListGetGtin14s'),
    path('ListRegistrarGTIN14/', views.ListRegistrarGTIN14, name='ListRegistrarGTIN14'),
    path("pt/", ptlist.as_view(), name="pt_list"),
    path("pt/<int:pk>/", ptdetail.as_view(), name="pt_detail"),
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