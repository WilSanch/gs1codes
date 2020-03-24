import collections
import json
import math
import re
import pandas as pd
import openpyxl
import uuid
import os.path
from django.db import transaction
from typing import TypedDict, List
from django.utils import timezone
from django.db import connection, transaction, IntegrityError
from administration.common.functions import Queries, Common
from administration.bussiness.models import *
from administration.common.constants import *
from datetime import datetime, timedelta
from azure.storage.blob import (
    BlockBlobService,
    ContainerPermissions,
    BlobPermissions,
    PublicAccess
)

def validaExcel(excel):
    ResponseValidateExcel = responseValidateExcel
        
    nombre, extension = os.path.splitext(excel.name)

    if  not (extension == ".xls" or extension == ".xlsx"):
        ResponseValidateExcel.valid = False
        ResponseValidateExcel.msj= 'Extension no valida ' + str(extension) +  ' las extensiones permitidas son .xls o .xlsx' 
        return ResponseValidateExcel
    
    excel_file = pd.ExcelFile(excel)
    
    dfs = {}
    for sheet in excel_file.sheet_names:
        dfs[sheet] = excel_file.parse(sheet)
    
    data = pd.DataFrame(dfs['Plantilla'])
    dataCantColumns = data.columns.size
    columnasexcel = ColumnsExcel
    
    if not dataCantColumns == len(columnasexcel):
        ResponseValidateExcel.valid = False
        ResponseValidateExcel.msj= 'Estructura de archivo incorrecta, revise e intente nuevamente. </br>Cantidad de columnas: ' + str(dataCantColumns) 
        return ResponseValidateExcel
    
    result = all (elem in columnasexcel for elem in data.columns)
    
    if not result:
        ResponseValidateExcel.valid = False
        ResponseValidateExcel.msj= 'Estructura de archivo incorrecta, revise e intente nuevamente. </br>Encabezados Incorrectos' 
        return ResponseValidateExcel
    
    ResponseValidateExcel.valid = True

    return ResponseValidateExcel

def cargaBlob(filename, binary):  
    
    try:  
        account_name = 'archivoscodigos'
        account_key = 'pbAL1EdRiappAAeF9T4y1DhJFT9/Bx0YpvR2CZ3x+UjEF1bfh28c+L3mDncz8jexX4/w6TUKNzMvHsXv59I7/A=='
        container_name = 'portafolionuevoasc'
        blob = BlockBlobService(account_name=account_name, account_key=account_key, socket_timeout=300)
        # upload file
        blob.create_blob_from_text(container_name, filename, binary)
        # publish file
        #permission = ContainerPermissions(read=True, write=True)
        token = blob.generate_blob_shared_access_signature(
            container_name,
            filename,
            BlobPermissions.READ,

            datetime.utcnow() + timedelta(hours=672))
        url = f"https://{account_name}.blob.core.windows.net/{container_name}/{filename}"   
        msj = 'Upload OK'
        return f"{url}?{token}"
    except Exception as error:
        data = {'Error message': str(error)}
        print('data_exception::', data)
        return data
