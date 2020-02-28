import json
from django.http import HttpResponse, JsonResponse
from administration.bussiness.prefix import activation,Test,inactivation
from rest_framework import generics
from administration.bussiness.codes import *
from administration.models.core import ProductType, GpcCategory, MeasureUnit
from django.views.decorators.csrf import csrf_exempt

class ptlist(generics.ListCreateAPIView):
      queryset = ProductType.objects.all() 
      serializer_class = ProductTypeSerializer

class ptdetail(generics.RetrieveDestroyAPIView):
      queryset = ProductType.objects.all() 
      serializer_class = ProductTypeSerializer

class ptcreate(generics.CreateAPIView):
      serializer_class = ProductTypeSerializer
      
class GetCategoriesGPC(generics.ListCreateAPIView):
      queryset = GpcCategory.objects.all() 
      serializer_class = GpcCategorySerializer

class GetMeasureUnits(generics.ListCreateAPIView):
      queryset = MeasureUnit.objects.all() 
      serializer_class = MeasureUnitsSerializer

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

def test(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(Test(json_data))
  
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