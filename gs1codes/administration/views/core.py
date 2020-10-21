import json
from django.http import HttpResponse, JsonResponse
from administration.bussiness.prefix_api import activation,inactivation,assignate_prefix,prefix_regroup,prefix_transfer,prefix_refund,masive_update_validity_date
from administration.bussiness.colabora import validate_gtin_by_nit, buscar_gln, get_gln_on_enterprise, get_gtin_by_nit_and_type_code, get_codigos_by_esquema, get_codigos_by_nit, saldos_by_nit, get_codigos_by_tipo_producto
from rest_framework import generics
from administration.bussiness.codes import *
from administration.models.core import ProductType, GpcCategory, MeasureUnit,Code
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

class ptlist(generics.ListCreateAPIView):
      queryset = ProductType.objects.all() 
      serializer_class = ProductTypeSerializer

class ptdetail(generics.RetrieveDestroyAPIView):
      queryset = ProductType.objects.all() 
      serializer_class = ProductTypeSerializer

class ptcreate(generics.CreateAPIView):
      serializer_class = ProductTypeSerializer
      
#class GetCategoriesGPC(generics.ListCreateAPIView):
#      queryset = GpcCategory.objects.all() 
#      serializer_class = GpcCategorySerializer

class GetMeasureUnits(generics.ListCreateAPIView):
      queryset = MeasureUnit.objects.all() 
      serializer_class = MeasureUnitsSerializer
      
@api_view(['POST'])
def UpdateCodigo(request):
  if request.method == 'POST':
    nit = request.data['Nit']
    id = request.data['Gtin']
    Gtin= int(str(id)[:-2])
    enterprise_obj = Enterprise.objects.get(identification=nit)
    prefix_objects = Prefix.objects.get(id_prefix=Gtin)
    if prefix_objects.enterprise_id == enterprise_obj.id :
      c = Code()
      c.id = id
      c.description = data=request.data['description']
      c.save(update_fields=['description'])
      return Response(data, status=status.HTTP_201_CREATED)


  
def mark(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(mark_codes(json_data))

def activate(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(activation(json_data))

def inactivate(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(inactivation(json_data))

def assignate(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(assignate_prefix(json_data))

def regroup(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(prefix_regroup(json_data))

def transfer(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(prefix_transfer(json_data))

def refund(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(prefix_refund(json_data))

def update_validity_date(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(masive_update_validity_date(json_data))
  
def get_gpc(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(get_gpc_category(json_data))

def RegistrarGTIN14(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(RegistryGtin14(json_data))
  

def GetGtin14s(request):
  if request.method == 'GET':
    if('Gtin' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})
    else:
      Gtin = request.GET['Gtin']
      return JsonResponse(GetGtin14sbyGtin13(Gtin))
  
def ListGetGtin14s(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(ListGetGtin14sGtin13(json_data))
  

def ListRegistrarGTIN14(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(ListRegistryGTIN14(json_data))

# Colabora -------------------------------------------------------

def ValidateGtinByNit(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(validate_gtin_by_nit(json_data))

def BuscaGlnNit(request):
  if request.method == 'GET':
    if('Gln' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})

    if('Nit' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})
    
    gln = request.GET['Gln']
    nit = request.GET['Nit']
    return JsonResponse(buscar_gln(gln,nit))

def GetGlnOnEnterprise(request):
  if request.method == 'GET':
    if('Gtin' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})
    
    gtin = request.GET['Gtin']
    return JsonResponse(get_gln_on_enterprise(gtin))

def GetGtinByNitAndTypeCode(request):
  if request.method == 'GET':
    if('Nit' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})
    
    nit = request.GET['Nit']
    return JsonResponse(get_gtin_by_nit_and_type_code(nit),safe=False)

def GetCodigosByEsquema(request):
  if request.method == 'GET':
    if('nit' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})

    if('prefix' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})
    
    nit = request.GET['nit']
    prefix =  request.GET['prefix']
    return JsonResponse(get_codigos_by_esquema(nit,prefix),safe=False)

def GetCodigosByNit(request):
  if request.method == 'GET':
    if('nit' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})

    if('pageIndex' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})

    if('countRegister' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})
    
    nit = request.GET['nit']
    pageIndex = request.GET['pageIndex']
    countRegister = request.GET['countRegister']
    return JsonResponse(get_codigos_by_nit(nit,pageIndex,countRegister),safe=False)

def SaldosByNit(request):
  if request.method == 'GET':
    if('nit' not in request.GET):
      return JsonResponse({"Error": "El parametro recibido no es el correcto."})

    nit = request.GET['nit']
    return JsonResponse(saldos_by_nit(nit),safe=False)

def GetCodigosByTipoProducto(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(get_codigos_by_tipo_producto(json_data))
