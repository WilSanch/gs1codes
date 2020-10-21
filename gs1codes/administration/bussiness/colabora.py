from django.shortcuts import render
from rest_framework import viewsets, filters
from administration.models.core import (Enterprise,Country,GpcCategory,MeasureUnit,Code)
from .colaboraSerializer import (EnterpriseSerializer,CountrySerializer,GpcCategorySerializer,MeasureUnitsSerializer,CodeSerializer)
from rest_framework import generics
from rest_framework.decorators import api_view

class EnterpriseView(generics.ListCreateAPIView):
    serializer_class = EnterpriseSerializer  
    queryset = Enterprise.objects.filter(enterprise_state=True) 
    #filter_backends = [filters.SearchFilter] 
    #search_fields = ['=nit'] 
    http_method_names = ['get']

class CountryView(generics.ListCreateAPIView):
    serializer_class = CountrySerializer 
    queryset = Country.objects.all() 
    #filter_backends = [filters.SearchFilter] 
    #search_fields = ['=nit'] 
    http_method_names = ['get']

class GpcCategoryView(generics.ListCreateAPIView):
    serializer_class = GpcCategorySerializer 
    queryset = GpcCategory.objects.all()
    http_method_names = ['get']

class MeasureUnitsView(generics.ListCreateAPIView):
    serializer_class = MeasureUnitsSerializer
    queryset = MeasureUnit.objects.all() 
    http_method_names = ['get']

class CodepriseView(generics.ListCreateAPIView):
    serializer_class = CodeSerializer  
    queryset = Code.objects.all()
    filter_backends = [filters.SearchFilter] 
    search_fields = ['=id'] 
    http_method_names = ['get']

@api_view(['GET'])
def GetGlnVerify(request):
    if request.method == 'GET':
        Gtin = request.data['Gtin']
        print(Gtin)
        code_obj = Code.objects.get(id=Gtin)
        return code_obj