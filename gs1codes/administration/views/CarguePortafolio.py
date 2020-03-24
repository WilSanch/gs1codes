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


@login_required 
@api_view(['GET','POST'])     
def cargue(request, format=None):
    if "GET" == request.method:
        return render(request, 'administration/frontTemplates/cargue.html', {})
    else:
        excel_file_upload = request.data["excel_file"]
        filename = excel_file_upload.name
        data = request.data["excel_file"].read()     
        #validacion estructura y extension del archivo excel.
        valida = validaExcel(excel_file_upload)
        
        if not (valida.valid):
            return render(request, 'administration/frontTemplates/cargue.html', {"Error": valida.msj}) 
                   
        cargaExcel = cargaBlob(filename, data)

        wb = openpyxl.load_workbook(excel_file_upload)

        # getting a particular sheet by name out of many sheets
        worksheet = wb["Plantilla"]
        print(worksheet)

        excel_data = list()
        # iterating over the rows and
        # getting value from each cell in row
        for row in worksheet.iter_rows():
            row_data = list()
            for cell in row:
                row_data.append(str(cell.value))
            excel_data.append(row_data)
            
        excel_data_head = excel_data[0]

    return render(request, 'administration/frontTemplates/cargue.html', {"excel_data":excel_data, "excel_data_head":excel_data_head})    
