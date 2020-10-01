from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from azure.storage.blob import (
    BlockBlobService,
    ContainerPermissions,
    BlobPermissions,
    PublicAccess
)
import datetime
from administration.bussiness.carguePortafolio import cargaBlob, listaArchivosBlob
from administration.bussiness.cargue_archivo import inactivacion_masiva,valida_excel,get_container_name,devolucion_masiva
from django.http import HttpResponse, Http404

account_name = 'archivoscodigos'
account_key = 'pbAL1EdRiappAAeF9T4y1DhJFT9/Bx0YpvR2CZ3x+UjEF1bfh28c+L3mDncz8jexX4/w6TUKNzMvHsXv59I7/A=='

@login_required 
@api_view(['GET','POST'])
def cargue_archivo(request, opc):
    opc = int(opc)
    if "GET" == request.method:
        container_name = get_container_name(opc)
        lista = listaArchivosBlob(container_name)

        context= {}
        context['opc'] = opc
        context['excel_data'] = list(lista)
        context['error_list'] = None
        context['Error'] = ""
        
        return render(request, 'administration/frontTemplates/cargue_archivo.html', {"contexto": context})
    else:
        excel_file_upload = request.data["excel_file"]
        # Se valida el excel
        msg_error = valida_excel(excel_file_upload)
        # Se obtiene el nombre del contenedor
        container_name = get_container_name(opc)

        context= {}
        context['opc'] = opc
        if (msg_error == ""):
            # Se sube el archivo al blob de azure
            data = request.data["excel_file"].read()
            result = cargaBlob(excel_file_upload.name,data,container_name)
            excel_file = request.FILES["excel_file"]

            if opc == 1:
                # Cargue archivo devolución
                error_list = devolucion_masiva(excel_file)
            elif opc == 2:
                # Inactivación masiva
                error_list = inactivacion_masiva(excel_file)
            else:
                return False

            # Se lista el blob
            lista = listaArchivosBlob(container_name)
            context['excel_data'] = list(lista)
            context['error_list'] = error_list
            context['Error'] = "Proceso completado. Verifica el registro de errores."
        else:
            # Se lista el blob
            lista = listaArchivosBlob(container_name)
            context['excel_data'] = list(lista)
            context['error_list'] = None
            context['Error'] = msg_error

        return render(request, 'administration/frontTemplates/cargue_archivo.html', {"contexto":context})    
