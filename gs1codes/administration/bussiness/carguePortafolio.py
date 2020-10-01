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
from administration.models.core import Enterprise, ProductType, Country, MeasureUnit, GpcCategory, TextilCategory, AtcCategory, ProductState,LogPortfolioUpload
from azure.storage.blob import (
    BlockBlobService,
    ContainerPermissions,
    BlobPermissions,
    PublicAccess
)
from administration.bussiness import codes as mcodes


def validaExcel(excel):
    ResponseValidateExcel = responseValidateExcel
        
    nombre, extension = os.path.splitext(excel.name)

    if  not (extension == ".xls" or extension == ".xlsx"):
        ResponseValidateExcel.valid = False
        ResponseValidateExcel.msj= 'Extension no valida ' + str(extension) +  ' las extensiones permitidas son .xls o .xlsx' 
        return ResponseValidateExcel
    
    
    if Enterprise.objects.filter(identification=nombre).count() <= 0:
        ResponseValidateExcel.valid = False
        ResponseValidateExcel.msj= 'Nit de empresa: ' + str(nombre) +  ' no existe en la Aplicacion.' 
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

def cargaBlob(filename, binary, container_name_tmp=None):  
    
    try:  
        account_name = 'archivoscodigos'
        account_key = 'pbAL1EdRiappAAeF9T4y1DhJFT9/Bx0YpvR2CZ3x+UjEF1bfh28c+L3mDncz8jexX4/w6TUKNzMvHsXv59I7/A=='
        
        if container_name_tmp == None:
            container_name = 'portafolionuevoasc'
        else:
            container_name = container_name_tmp

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

def listaArchivosBlob(container_name_tmp=None):
    try:  
        account_name = 'archivoscodigos'
        account_key = 'pbAL1EdRiappAAeF9T4y1DhJFT9/Bx0YpvR2CZ3x+UjEF1bfh28c+L3mDncz8jexX4/w6TUKNzMvHsXv59I7/A=='
        if container_name_tmp == None:
            container_name = 'portafolionuevoasc'
        else:
            container_name = container_name_tmp
        blob = BlockBlobService(account_name=account_name, account_key=account_key, socket_timeout=300)
        listaArchivos = blob.list_blobs(container_name)
        lista =[]
        for blob in listaArchivos:
            fecha_blob = blob.properties.creation_time
            lista.append({
                "nombre": blob.name,
                "fecha": str(blob.properties.creation_time),
                "fecha_formato": str(fecha_blob.day).zfill(2) + "/" + str(fecha_blob.month).zfill(2) + "/" + str(fecha_blob.year) + " " + str(fecha_blob.hour).zfill(2) + ":" + str(fecha_blob.minute).zfill(2) + ":" + str(fecha_blob.second).zfill(2)
            })
            if container_name_tmp == None:
                print("\t" + blob.name + ' ' + str(blob.properties.creation_time))
            
        return lista
    except Exception as error:
        data = {'Error message': str(error)}
        print('data_exception::', data)
        return data

def ProcesarBlob():
    try:
        local_path = "../filesPortafolio"  
        account_name = 'archivoscodigos'
        account_key = 'pbAL1EdRiappAAeF9T4y1DhJFT9/Bx0YpvR2CZ3x+UjEF1bfh28c+L3mDncz8jexX4/w6TUKNzMvHsXv59I7/A=='
        container_name = 'portafolionuevoasc'
        BASE = os.path.dirname(os.path.abspath(__file__))
        download_files = os.path.join(BASE, 'filesPortafolio')
        blob = BlockBlobService(account_name=account_name, account_key=account_key, socket_timeout=300)
        listaArchivos = blob.list_blobs(container_name)
        lista =[]
        for blobf in listaArchivos:
            nombre, extension = os.path.splitext(blobf.name)
            blobFile = blob.get_blob_to_bytes(container_name,blobf.name)
            download_file_path = os.path.join(download_files, blobFile.name)
            print("\nDownloading blob to \n\t" + download_file_path)
            with open(download_file_path, "wb") as download_file:
                download_file.write(blobFile.content)
            wb = openpyxl.load_workbook(download_file_path)
            excel_file = pd.ExcelFile(download_file_path)
            dfs = {}
            for sheet in excel_file.sheet_names:
                dfs[sheet] = excel_file.parse(sheet)            
            data = pd.DataFrame(dfs['Plantilla'])
            excelTransform(data,nombre)                
        return lista
    except Exception as error:
        data = {'Error message': str(error)}
        print('data_exception::', data)
        return data

def excelTransform(excel,Nit):
    try:    
        GTINS13 = excel[excel['GtinPadre'] == 0]
        MarkGtin13 = markGtin13(GTINS13,Nit)        
        GTINS14 = excel[excel['GtinPadre'] != 0]
        MarkGtin14 = markGtin14(GTINS14,Nit)  
        return 'ok'
    except Exception as error:
        data = {'Error message': str(error)}
        print('data_exception::', data)
        return data

def markGtin13(df,Nit):
    jsonGtin13={"Nit":Nit,
            "TipoProducto": 1,
            "Username": "10203040"}
    jsonGtin13['Esquemas']=[2,3,6]
    jsonGtin13['Codigos']=[]
    for index, row in df.iterrows():
        gpc=''
        textil=''
        tipoProducto = ProductType.objects.filter(description=row['TipoProducto'])[0].id
        if tipoProducto == ProductTypeCodes.Producto.value:
            gpc = GpcCategory.objects.filter(spanish_name_brick=row['CategoriaLogyca'])[0].brick_code
        if tipoProducto == ProductTypeCodes.Farmaceutico.value:
            gpc = AtcCategory.objects.filter(name=row['CategoriaLogyca'])[0].code
        if tipoProducto == ProductTypeCodes.Textil.value:
            textil = row['CategoriaLogyca']
        jsonGtin13['Codigos'].append({
            "Codigo": row['Gtin'],
            "Descripcion": row['DescripcionLarga'],
            "TipoProducto": tipoProducto,
            "Brand":row['Marca'],
            "TargetMarket": Country.objects.filter(name=row['MercadoObjetivo'])[0].iso_a3,
            "Gpc":gpc,
            "Textil":textil,
            "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
            "State": ProductState.objects.filter(description=row['EstadoProducto'])[0].id,
            "MeasureUnit": MeasureUnit.objects.filter(description=row['UnidadMedida'])[0].id,
            "Quantity":row['CantidadEnvase']})    
    rta = mcodes.mark_codes(jsonGtin13)
    insert_LogPortfolioUpload(rta,Nit)
    print(rta)
    return rta
    
def insert_LogPortfolioUpload(rta,Nit):
    try: 
        lp = LogPortfolioUpload()
        lp.id
        lp.nit=(Nit)
        lp.user = ("CARLOS")
        lp.execution_date = timezone.now()
        lp.reply = (rta)
        lp.save()
        return "log ok"
    except Exception:
        return print("error al cguardar log")

def markGtin14(df,Nit):
    rta = {}
    rta['Request'] = []
    for index, row in df.iterrows():
        jsonGtin14={
            "idGtin13" : row['GtinPadre'],
            "idGtin14" : row['Gtin'],
            "descripcion" : row['DescripcionLarga'],
            "cantidad" : row['CantidadEnvase'],
            "nit" : Nit
        }
        res = mcodes.RegistryGtin14(jsonGtin14)
        rta['Request'].append(res)    
    print(rta)

def logPortfolioUploadList(idPk):
    try:
        return LogPortfolioUpload.objects.filter(nit=idPk)
    except IntegrityError:
        return False