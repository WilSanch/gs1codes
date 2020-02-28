# %%
# from explorations import setup_django
from IPython.extensions import autoreload
%load_ext autoreload
%autoreload 2
import math
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
cod = Code.objects.filter(id = 7707007099787).filter(state_id=2)
cod1= Code.objects.filter(id = 7707007099787)[0].id

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
