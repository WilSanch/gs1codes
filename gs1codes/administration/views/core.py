import json
from django.http import HttpResponse, JsonResponse
from administration.bussiness.codes import mark_codes
from administration.bussiness.prefix import activation,Pruebas
from rest_framework import generics
from administration.bussiness.codes import mark_codes, get_gpc_category, ProductTypeSerializer, GpcCategorySerializer, MeasureUnitsSerializer
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

class GetCategoriesGPC(generics.ListCreateAPIView):
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

def pruebas(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(Pruebas(json_data))
  
def get_gpc(request):
  if request.method == 'POST':
    json_data = json.loads(request.body)
    return JsonResponse(get_gpc_category(json_data))
