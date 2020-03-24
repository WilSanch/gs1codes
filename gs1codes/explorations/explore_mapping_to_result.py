# %%
# from explorations import setup_django
from IPython.extensions import autoreload
%load_ext autoreload
%autoreload 2
import math
import requests
import timeit
import collections
import sys
import os
import django
import json
import pandas as pd
sys.path.extend([os.path.dirname(os.getcwd())])
django.setup()
from administration.common.constants import *
from administration.common.functions import Common, Queries
from django.db import connection
import pandas as pd
from administration.models.core import *
from administration.bussiness import codes as mcodes
import time
#%%
import random
Nit='10203040'
Cantidad=100

jsonPrb={"Nit":Nit,
    "TipoProducto": 1,
    "Username": "10203040"}
jsonPrb['Esquemas']=[2,3,6]
jsonPrb['Codigos']=[]

for codigo in range(Cantidad):    
    jsonPrb['Codigos'].append({
        "Descripcion": f"Prod.Prb05-{codigo+1}",
        "TipoProducto": 1,
        "Brand":"Generico",
        "TargetMarket":"COL",
        "Gpc":"10001682",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit":int("{0:.0f}".format(random.uniform(1,49))),
        "Quantity":float("{0:.2f}".format(random.uniform(1,10)))})    

# rta = mcodes.mark_codes(jsonPrb)
# print(rta)
with  open("D:\\PrbJson\\PruebasJsonMarcacion.json", "w+") as file:
    json.dump(jsonPrb, file, indent=True)

# %%
gtin14 = '37707007099788'
print(gtin14)
gtin14sinEsq = gtin14[ 1:len(gtin14) - 1]
print(gtin14sinEsq)
id_code = Common.CalculaDV(gtin14sinEsq)
print(id_code)

# %%
q1 = '''
        SELECT 
            ID,
            ID_CODE_id,
            QUANTITY
        FROM administration_code_gtin14 acg 
        WHERE ID_CODE_id = '{}';
        '''.format(7707007099787)
        
cursor= connection.cursor()
cursor.execute(q1)
Gtin14Gtin13 =  dfCodesGtin14Gtin13(data=cursor.fetchall())
cant = Gtin14Gtin13[Gtin14Gtin13['quantity']==2]
DupGtin14 = Gtin14Gtin13[Gtin14Gtin13['id']==17707007099784]
print(Gtin14Gtin13)
# %%
q1 = Queries.GetGetin14s('7707007099787')

cursor= connection.cursor()
cursor.execute(q1)
Gtin14Gtin13 =  dfCodesGtin14s(data=cursor.fetchall())
Gtin14DataBM = []

for row_index, row in Gtin14Gtin13.iterrows():
    Gtin14DataBM.append(
        {
           "IdGtin14": row['id'],
           "IdGtinBase":row['id_code_id'],
           "Descripcion":row['description'],
           "Cantidad":row['quantity']
        }
    )

#%%
url = "https://testpowerbiapi.azurewebsites.net/api/User/PowerBI?WorkspaceId=3c149686-3b16-40be-b187-0bb1df10b31e&ReportId=a2107dac-b314-45b1-9b1c-c585a13a8178"
response = requests.get(url)
res = response.content

my_json = res.decode('utf8').replace("'", '"')

data = json.loads(my_json)
token = data['embedToken']['token']
rptUrl = data['rptUrl']
rptId = data['rptId']
# %%
g14s = mcodes.getGtin14byNit(10203040)

# %%
# Create a file in local Documents directory to upload and download
import uuid
from azure.storage.blob import BlobServiceClient

connect_str = "DefaultEndpointsProtocol=https;AccountName=archivoscodigos;AccountKey=pbAL1EdRiappAAeF9T4y1DhJFT9/Bx0YpvR2CZ3x+UjEF1bfh28c+L3mDncz8jexX4/w6TUKNzMvHsXv59I7/A=="
blob_service_client = BlobServiceClient.from_connection_string(connect_str)

# Create a unique name for the container
container_name = "quickstart" + str(uuid.uuid4())

# Create the container
container_client = blob_service_client.create_container(container_name)

# Create a file in local Documents directory to upload and download
local_path = "./data"
local_file_name = "quickstart" + str(uuid.uuid4()) + ".txt"
upload_file_path = os.path.join(local_path, local_file_name)

# Write text to the file
file = open(upload_file_path, 'w')
file.write("Hello, World!")
file.close()

# Create a blob client using the local file name as the name for the blob
blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

# Upload the created file
with open(upload_file_path, "rb") as data:
    blob_client.upload_blob(data)
    
# Download the blob to a local file
# Add 'DOWNLOAD' before the .txt extension so you can see both files in Documents
download_file_path = os.path.join(local_path, str.replace(local_file_name ,'.txt', 'DOWNLOAD.txt'))
print("\nDownloading blob to \n\t" + download_file_path)

with open(download_file_path, "wb") as download_file:
    download_file.write(blob_client.download_blob().readall())
# %%
import openpyxl
ipath = './/data//Prb.xlsx'
doc = openpyxl.load_workbook(ipath)
hoja = doc.get_sheet_by_name('Plantilla')

# %%
seleccion = hoja['A1':'K1']
for filas in seleccion:
    for columnas in filas:
        print(columnas.coordinate, columnas.value)
    print("--Final de fila--")

# %%
