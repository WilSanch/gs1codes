# %%
# from explorations import setup_django
%load_ext autoreload
%autoreload 2
import timeit
import sys
import os
import django
sys.path.extend([os.path.dirname(os.getcwd())])
django.setup()
from administration.common.constants import StateCodes
from administration.common.functions import Common, Queries
from django.db import connection
import pandas as pd
from administration.models.core import *

# %%
Enterprise.objects.select_related('country')\
    .values('id',
            'enterprise_name',
            'country__name')\
    .get(id=2)

# %%
ent = Enterprise.objects.select_related('prefix',)\
.values('id','prefix','prefix__range_id')
print(ent.query)


# %%

q1= Queries.CodesbyNitbyProductType('10203040', StateCodes().Asignado)
cursor = connection.cursor()
cursor.execute(q1)
pand = pd.DataFrame(cursor.fetchall(),columns=['ProductTypeId','Description','CantGLN'])
pand
# %%
q2 =  Queries.PrefixBySchema('10203040')
cursor = connection.cursor()
cursor.execute(q2)
pand2 = pd.DataFrame(cursor.fetchall(),columns=['id','description'])
pand2.set_index('id')
# %%
%%time
r=4

# %%
# 7707335210045
GTIN_SDV='770733521004'
factor=3
sum=0
e = len(GTIN_SDV)-1
 
while e>=0:
    sum=sum + int(GTIN_SDV[e]) *  factor
    factor = 4-factor
    e=e-1

dv=(1000 - sum) % 10
GTIN_CDV = GTIN_SDV + str(dv)
GTIN_CDV

# %%
r=2
pref = Common.PrefixGenerator(r)
cat:Range = Range.objects.get(id=r)

x=cat.quantity_code
y= len(str(x))-1

display(pref)

listCodes =[]

for c in range(x):
    csdv = str(pref) + str(c).zfill(y)
    ccdv = Common.CalculaDV(csdv)
    listCodes.append(ccdv)
    
len(listCodes)
# %%
%time
range_id=3
prefFn = Common.PrefixGenerator(range_id)
listCodeFn = Common.CodeGenerator(prefFn,range_id)

display(prefFn)
listCodeFn
# %%
insPref :  Prefix =  Prefix()
insPref.id_prefix = int(prefFn)
insPref.observation ='Pruebas Creacion'
insPref.range = Range.objects.get(id=range_id)
insPref.state = State.objects.get(id=2)
insPref.save()

#%%
%%time
bulk_code=[]

for cod in listCodeFn:
    new_code: Code = Code()
    new_code.id = cod
    new_code.state = State.objects.get(id=1)
    new_code.prefix = Prefix.objects.get(id_prefix=prefFn)
    bulk_code.append(new_code)

Code.objects.bulk_create(bulk_code)

# %%
cursor = connection.cursor()
spv = Queries.AvailableCodes('10203040', True)
conn = connection.connection
cursor = conn.cursor()
cursor.execute(spv)
value = cursor.fetchone()[0]
value

# %%
 mark= {  
  	"Codigos": [{
        "Codigo": 7709134070578,
        "Descripcion": "Calostro bovino",
        "Id": 0,
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10003157",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 12,
        "Quantity": 450.0,
    },
    {
        "Codigo": 7709134070576,
        "Descripcion": "Producto 2",
        "Id": 0,
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10000467",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 1,
        "Quantity": 450.0,
    },
    {
        "Descripcion": "Producto 2",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
        "Prefix": "770123"
    },
    {
        "Descripcion": "Producto PV",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
    }],
    "Esquemas": [1, 2, 3, 6],
    "Nit": "10203040",
    "TipoProducto": 1
}
# %%
codesMark = mark['Codigos']
df = pd.DataFrame(data=codesMark)
df2 = df.groupby('TipoProducto')

df2.get_group(1)

# %%
for TipoProducto, Codigo in df2:
    # print('\nCREATE TABLE {}('.format(TipoProducto)) 
    for row_index, row in Codigo.iterrows():

        print('\n {} {} {}'.format(row['Codigo'],row['Descripcion'],row['TipoProducto']))
        
# %%
