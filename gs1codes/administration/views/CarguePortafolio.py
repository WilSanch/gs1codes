from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from administration.bussiness import codes as mcodes
import pandas as pd
import json
import openpyxl
import uuid
import os.path
from administration.bussiness.carguePortafolio import *
from django.http import HttpRequest, HttpResponse, JsonResponse
from rest_framework.views import APIView
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.core import serializers

@login_required 
@api_view(['GET','POST'])     
def cargue(request, format=None):
    if "GET" == request.method:
        lista = listaArchivosBlob()
        return render(request, 'administration/frontTemplates/cargue.html', {"excel_data": lista})
    else:
        excel_file_upload = request.data["excel_file"]
        filename = excel_file_upload.name
        data = request.data["excel_file"].read()
        #validacion estructura y extension del archivo excel.
        valida = validaExcel(excel_file_upload)
        
        if not (valida.valid):
            return render(request, 'administration/frontTemplates/cargue.html', {"Error": valida.msj}) 
        
        #Carga archivo al blob           
        cargaExcel = cargaBlob(filename, data)
        lista = listaArchivosBlob()

    return render(request, 'administration/frontTemplates/cargue.html', {"excel_data":lista})    

@login_required 
@api_view(['GET','POST'])     
def procesaBlobs(request, format=None):
    rta = ProcesarBlob()
    msj = {"mensaje":"Blobs Procesados"}
    return JsonResponse(msj) 

@login_required 
@api_view(['GET', 'POST'])
def loadResultList(request, format=None):
    if "GET" == request.method:
        return render(request, 'administration/frontTemplates/cargue_resultado.html')
    if "POST" == request.method:
        nit = request.POST['nit']
        pf = logPortfolioUploadList(nit)
        dictionaries = [ obj for obj in pf.values() ]        
        return JsonResponse({"data": dictionaries}, safe=False)
