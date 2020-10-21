from django.shortcuts import render
from rest_framework import viewsets, filters
from administration.models.core import (Enterprise,Country,GpcCategory,MeasureUnit,Code,Prefix)
from .colaboraSerializer import (EnterpriseSerializer,CountrySerializer,GpcCategorySerializer,MeasureUnitsSerializer,CodeSerializer)
from rest_framework import generics
from rest_framework.decorators import api_view
from datetime import datetime
from django.db import transaction
from administration.bussiness.models import ObjectIsValidGtin, IsValidGtinByNit, BuscarGln, glnEnterprise, ListGtinByNitTypeCode, CodigosByEsquema, Gtin13DescriptionColabora, CodigosColabora, ListaPrefMarcacionSaldos, SaldosPrefijo, QueryPagination
from django.shortcuts import get_object_or_404
from administration.common.constants import StCodes, SchemaCodes, ProductType
from django.db.models import F,Q,Sum,Count
from typing import List
from django.http import Http404

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


def validate_gtin_by_nit(gtins: ObjectIsValidGtin) -> ObjectIsValidGtin:
    obj_enterprise = get_object_or_404(Enterprise,identification=gtins['Nit'] )
    
    lista_gtin = []

    for gtin in gtins['Gtins']:
        obj_code = Code.objects.filter(id=gtin['Gtin'],state_id=StCodes.Asignado.value).first()
        if (obj_code is not None):
            obj_prefix = Prefix.objects.filter(id=obj_code.prefix_id,enterprise_id=obj_enterprise.id)
        else:
            obj_prefix = None

        obj_gtin = IsValidGtinByNit()
        obj_gtin['Gtin'] = int(gtin['Gtin'])

        if (obj_code is None or obj_prefix is None):
            obj_gtin['IsValid'] = False
            obj_gtin['Status'] = str(StCodes.Disponible.value)
            obj_gtin['TypeProduct'] = ""
        else:
            obj_gtin['IsValid'] = True
            obj_gtin['Status'] = str(obj_code.state_id)
            obj_gtin['TypeProduct'] = str(obj_code.product_type_id)
        
        lista_gtin.append(obj_gtin)

    obj_gtin_nit = ObjectIsValidGtin()
    obj_gtin_nit['Gtins'] = lista_gtin
    obj_gtin_nit['Nit'] = gtins['Nit']

    return obj_gtin_nit
        
def buscar_gln(gln: int, nit: str) -> BuscarGln:
    obj_enterprise = get_object_or_404(Enterprise,identification=nit)
    
    #select_related,prefetch_related
    obj_code = Code.objects.select_related('prefix').filter(id=gln,prefix__enterprise_id=obj_enterprise.id).first()
    
    obj_gln = BuscarGln()
    obj_gln['Gln'] = gln
    obj_gln['ProducType'] = obj_code.product_type_id

    return obj_gln

def get_gln_on_enterprise(gtin: int) -> glnEnterprise:
    obj_code = Code.objects.annotate(state_desc=F('state__description')).filter(id=gtin).first()
    obj_prefix = Prefix.objects.annotate(enterprise_name=F('enterprise__enterprise_name'), enterprise_nit=F('enterprise__identification')).filter(id=obj_code.prefix_id).first()
    
    obj_gln = glnEnterprise()
    obj_gln['Nit'] = obj_prefix.enterprise_nit
    obj_gln['Name'] = obj_prefix.enterprise_name
    obj_gln['Gtin'] = obj_code.id
    obj_gln['StateGtin'] = obj_code.state_desc

    return obj_gln

def get_gtin_by_nit_and_type_code(Nit: str) -> List[ListGtinByNitTypeCode]:
    obj_enterprise = get_object_or_404(Enterprise,identification=Nit)

    obj_prefix = Prefix.objects.filter(enterprise_id=obj_enterprise.id,state_id=StCodes.Asignado.value)
    obj_prefix_31_dic = obj_prefix.filter(Q(schema_id=SchemaCodes.RenovacionAnual31Diciembre.value) | Q(schema_id=SchemaCodes.RenovacionAnual31DiciembreGs1.value))
    obj_prefix_99_anos = obj_prefix.filter(schema_id=SchemaCodes.Renovacion99Años.value)
    
    Lista = []
    for pr in obj_prefix_31_dic:
        obj_gtin = ListGtinByNitTypeCode()

        obj_gtin['CompanyName'] = obj_enterprise.enterprise_name
        obj_gtin['Gtin'] = 0
        obj_gtin['Nit'] = Nit
        obj_gtin['Prefix'] = pr.id_prefix
        obj_gtin['ProductName'] = ""
        obj_gtin['IsMember'] = True
        obj_gtin['TypeDescription'] = ""
        obj_gtin['IsGtin13'] = False
        obj_gtin['AssigmentDate'] = pr.assignment_date
        obj_gtin['ValidityDate'] = pr.validity_date

        Lista.append(obj_gtin)

    for pr in obj_prefix_99_anos:
        obj_code = Code.objects.filter(prefix_id=pr.id,state_id=StCodes.Asignado.value).filter(Q(product_type_id=ProductType.Producto.value) | Q(product_type_id=ProductType.Recaudo.value) | Q(product_type_id=ProductType.Gln.value) | Q(product_type_id=ProductType.Textil.value) | Q(product_type_id=ProductType.Farmaceutico.value))

        for cd in obj_code:
            obj_gtin = ListGtinByNitTypeCode()

            obj_gtin['CompanyName'] = obj_enterprise.enterprise_name
            obj_gtin['Gtin'] = cd.id
            obj_gtin['Nit'] = Nit
            obj_gtin['Prefix'] = pr.id_prefix
            obj_gtin['ProductName'] = cd.description
            obj_gtin['IsMember'] = False
            obj_gtin['TypeDescription'] = str(cd.product_type)
            obj_gtin['IsGtin13'] = False

            Lista.append(obj_gtin)
    
    return Lista

def get_codigos_by_esquema(nit: str, prefix: str) -> List[CodigosByEsquema]:
    obj_prefix = Prefix.objects.filter(id_prefix=prefix,enterprise__identification=nit).annotate(purchased=Sum('code_quantity_purchased'),consumed=Sum('code_quantity_consumed'),reserved=Sum('code_quantity_reserved'),schema_name=F('schema__description'))

    Lista = []
    for pr in obj_prefix:
        obj_codes = CodigosByEsquema()
        obj_codes['IdEsquema'] = pr.schema_id
        obj_codes['Esquema'] = pr.schema_name
        obj_codes['CodigosComprados'] = pr.purchased
        obj_codes['CodigosAsignados'] = pr.consumed
        obj_codes['CodigosDisponibles'] = pr.reserved

        Lista.append(obj_codes)

    return Lista

def get_codigos_by_nit(nit: str, pageIndex: int, countRegister: int) -> List[CodigosColabora]:
    obj_enterprise = get_object_or_404(Enterprise,identification=nit)
    obj_code = Code.objects.filter(prefix__enterprise_id=obj_enterprise.id,state_id=StCodes.Asignado.value,prefix__state_id=StCodes.Asignado.value)[int(pageIndex):int(countRegister)]

    if not obj_code:
        return Http404

    Lista_code = []

    obj_colabora = CodigosByEsquema()
    obj_colabora['TotalRegistros'] = obj_code.count()

    for cd in obj_code:
        obj_code_list = Gtin13DescriptionColabora()
        obj_code_list['Codigo'] = cd.id
        obj_code_list['Descripcion'] = cd.description
        obj_code_list['TipoProducto'] = cd.product_type_id
        obj_code_list['FechaAsignacion'] = cd.assignment_date
        obj_code_list['EstadoProducto'] = cd.product_state_id

        Lista_code.append(obj_code_list)

    obj_colabora['gtin13Descriptions'] = Lista_code

    Lista_colabora = []
    Lista_colabora.append(obj_colabora)
      
    return Lista_colabora

def saldos_by_nit(nit: str) -> List[ListaPrefMarcacionSaldos]:
    obj_prefix = Prefix.objects.filter(enterprise__identification=nit,state_id=StCodes.Asignado.value).annotate(total_prefijo=F('range__quantity_code'))

    if not obj_prefix:
        return Http404

    Lista_prefix = []

    for pr in obj_prefix:
        obj_saldos = ListaPrefMarcacionSaldos()
        obj_saldos['Prefix'] = pr.id_prefix
        obj_saldos['TotalPrefijo'] = pr.total_prefijo

        obj_code = Code.objects.filter(prefix_id=pr.id).values('state_id').annotate(cantidad=Count('state_id'))
        Lista_code = []

        for cd in obj_code:
            obj_codes_by_state = SaldosPrefijo()
            obj_codes_by_state['Estado'] = cd['state_id']
            obj_codes_by_state['Cantidad'] = cd['cantidad']

            Lista_code.append(obj_codes_by_state)

        obj_saldos['CantidadPorEstado'] = Lista_code
        Lista_prefix.append(obj_saldos)

    return Lista_prefix

def get_codigos_by_tipo_producto(query: QueryPagination) -> CodigosColabora:
    obj_enterprise = get_object_or_404(Enterprise,identification=query['Nit'])
    obj_code = Code.objects.filter(prefix__enterprise_id=obj_enterprise.id,state_id=query['State'],prefix__state_id=StCodes.Asignado.value).filter(product_type_id__in=query['ProductTypes'])[query['PageIndex']:query['CountRegister']]
    
    if not obj_code:
        return Http404

    Lista_code = []

    obj_colabora = CodigosByEsquema()
    obj_colabora['TotalRegistros'] = obj_code.count()

    for cd in obj_code:
        obj_code_list = Gtin13DescriptionColabora()
        obj_code_list['Codigo'] = cd.id
        obj_code_list['Descripcion'] = cd.description
        obj_code_list['TipoProducto'] = cd.product_type_id
        obj_code_list['FechaAsignacion'] = cd.assignment_date
        obj_code_list['EstadoProducto'] = cd.product_state_id

        Lista_code.append(obj_code_list)

    obj_colabora['gtin13Descriptions'] = Lista_code

    return obj_colabora
