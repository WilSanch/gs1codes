from django.shortcuts import render
from rest_framework.decorators import api_view
from django.contrib.auth.decorators import login_required
from administration.models.core import (Prefix,Code,Enterprise)
from django.http import JsonResponse
from django.db import IntegrityError
# Create your views here.

def status_code(idPk):
    try:
        return Code.objects.filter(id=idPk)
    except IntegrityError:
        return False
def status_prefix(idpk):
    try:
        return Prefix.objects.filter(id_prefix=idpk)
    except IndentationError:
        return False
        
@login_required 
@api_view(['GET', 'POST'])
def status_pre_cod(request,format=None):
    if "GET" == request.method:
        return render(request, './reports/status_pre_cod.html')
    if "POST" == request.method:
        id = request.POST['id']
        option = request.POST['option']
        if option == "Codigo":
            cod = status_code(id)
            dictionaries = [ obj for obj in cod.values(
                "prefix_id__id_prefix","prefix_id__observation",
                "prefix_id__schema_id__description","description","state_id__description",
                "prefix_id__enterprise_id__identification","prefix_id__enterprise_id__enterprise_name",
                "assignment_date","prefix_id__validity_date","product_type_id__description","id"
                ) ]        
            return JsonResponse({"data": dictionaries}, safe=False)
        if( option == "Prefijo"):
            pre = status_prefix(id)
            dictionaries = [ obj for obj in pre.values(
                "id_prefix","state_id__description","schema_id__description","enterprise_id__identification","enterprise_id__enterprise_name",
                "assignment_date","validity_date","range_id__name"
            ) ]   
            return JsonResponse({"data": dictionaries}, safe=False)


def codEnterprise(idpk):
    try:
        return Code.objects.filter(prefix_id__enterprise_id__identification=idpk)
    except IndentationError:
        return False

@login_required 
@api_view(['GET', 'POST'])
def codxEnterprise(request,format=None):
    if "GET" == request.method:
        return render(request, './reports/cod_x_enterprise.html')
    if "POST" == request.method:
        nit = request.POST['nit']
        ent = codEnterprise(nit)
        #idempresa = ent.values("id")
        dictionaries = [ obj for obj in ent.values(
            "id","prefix_id__enterprise_id__enterprise_name","prefix_id__enterprise_id__identification",
            "prefix_id__id_prefix","prefix_id__schema_id__description",
            "description","state_id__description","assignment_date",
            "prefix_id__validity_date","product_type_id__description"
        ) ]        
        return JsonResponse({"data": dictionaries}, safe=False)