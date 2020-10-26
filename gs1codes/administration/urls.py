from django.urls import path
from . import views
from administration.views.core import ptlist,ptdetail,UpdateCodigo,InactivaProductos
from administration.views.prefix import (load_enterprise,updateAdList,updateAd)
from rest_framework_swagger.views import get_swagger_view
from django.views.generic import TemplateView
from django.conf.urls import url
from administration.views.CarguePortafolio import (loadResultList)
from django.conf import settings
from django.conf.urls.static import static
from administration.bussiness.colabora import (EnterpriseView,CountryView,GpcCategoryView,MeasureUnitsView,CodepriseView)
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
    path('enterprise_modify/<str:enterprise>/', views.enterprise_modify, name='enterprise_modify'),
    path('RegistrarGTIN14/', views.RegistrarGTIN14, name='RegistrarGTIN14'),
    path("pt/", ptlist.as_view(), name="pt_list"),
    path("pt/<int:pk>/", ptdetail.as_view(), name="pt_detail"),
    #path("GetCategoriesGPC/", GetCategoriesGPC.as_view(), name="GetCategoriesGPC"),
    #path("GetMeasureUnits/", GetMeasureUnits.as_view(), name="GetMeasureUnits"),
    path('ejemplo/', views.ejemplo, name='ejemplo'),
    path('nit1/', views.nit1, name='nit1'),
    path('report/', views.report, name='report'),
    path('PowerBI/', views.reportPowerBI, name='PowerBI'),
    path('Cargue/', views.cargue, name='Cargue'),
    path('cargue_resultado/', loadResultList, name='cargue_resultado'),
    path('cargue_archivo/<opc>/', views.cargue_archivo, name='CargueArchivo'), 
    url(r'^updateAdList/(?P<enterprise_nit>[-a-zA-Z0-9_]+)/$', updateAdList, name='updateAdList'),
    path('update_ad/', updateAd, name='update_ad'),
    path('CodigosByEmpresa/ValidateGtinByNit/', views.ValidateGtinByNit, name='ValidateGtinByNit'),
    path('BuscaGlnNit/', views.BuscaGlnNit, name='BuscaGlnNit'),
    path('GetGlnOnEnterprise/', views.GetGlnOnEnterprise, name='GetGlnOnEnterprise'),
    path('GTIN14/ListRegistrarGTIN14/', views.ListRegistrarGTIN14, name='ListRegistrarGTIN14'),
    path('CodigosByEmpresa/GetGtinByNitAndTypeCode/', views.GetGtinByNitAndTypeCode, name='GetGtinByNitAndTypeCode'),
    path('CodigosByEmpresa/GetCodigosByEsquema/', views.GetCodigosByEsquema, name='GetCodigosByEsquema'),
    path('CodigosByEmpresa/GetCodigosByNit/', views.GetCodigosByNit, name='GetCodigosByNit'),
    path('SaldosByNit/', views.SaldosByNit, name='SaldosByNit'),
    path('CodigosByEmpresa/GetCodigosByTipoProducto/', views.GetCodigosByTipoProducto, name='GetCodigosByTipoProducto'),
    path('GTIN14/GetGtin14s/', views.GetGtin14s, name='GetGtin14s'),
    path('GTIN14/ListGetGtin14s/', views.ListGetGtin14s, name='ListGetGtin14s'),
    path('ProcesaBlobs/', views.procesaBlobs, name='ProcesaBlobs'),
    path('swagger-docs/', schema_view),
    #colabora
    path('GetGlnVerify/', views.GetGlnVerify, name='GetGlnVerify'),
    path('GetPrefList/', views.GetPrefList, name='GetPrefList'),
    path('Empresa/GetAll/', EnterpriseView.as_view(), name='Empresa_GetAll'),
    path('GetTargetMarket/', CountryView.as_view(), name='GetTargetMarket'),
    path('UpdateCodigo/', UpdateCodigo, name='UpdateCodigo'),
    path('InactivaProductos/', InactivaProductos, name='InactivaProductos'),
    path('GetCategoriesGPC/', GpcCategoryView.as_view(), name='GetCategoriesGPC'),
    path("GetMeasureUnits/", MeasureUnitsView.as_view(), name="GetMeasureUnits"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)