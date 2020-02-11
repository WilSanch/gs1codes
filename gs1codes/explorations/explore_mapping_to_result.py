# %%
# from explorations import setup_django
%load_ext autoreload
%autoreload 2
import math
import timeit
import collections
import sys
import os
import django
import pandas as pd
sys.path.extend([os.path.dirname(os.getcwd())])
django.setup()
from administration.common.constants import *
from administration.common.functions import Common, Queries
from django.db import connection
import pandas as pd
from administration.models.core import *

# %%
 mark= {  
  	"Codigos": [{
        "Codigo": 7703742071705,
        "Descripcion": "Producto 1",
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
        "Codigo": 7703742071767,
        "Descripcion": "Producto 2",
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
        "Descripcion": "Producto 3",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
        "Prefix": 77037423894
    },
    {
        "Descripcion": "Producto 4",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
    },
    {
        "Descripcion": "Producto 5",
        "TipoProducto": 7,
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
def Mark_Code_fn(Code):
    q1 = Queries.codObj(Code,'10203040')
    print(q1)
    cursor= connection.cursor()
    cursor.execute(q1)
    CodObj =  pd.DataFrame(cursor.fetchall())
    CodObj.head()
# %%
auto=0
codManuales =[]
for TipoProducto, Codigo in df2:
    
    for row_index, row in Codigo.iterrows():
        if (not math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            codManuales.append(row['Codigo'])
            
        if (math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            auto = auto + 1 
            
    for row_index, row in Codigo.iterrows():
        if (not math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            print('\n {} {} {} {} {}'.format(row['Codigo'],row['Descripcion'],row['TipoProducto'],row['Prefix'] ,'AsignacionManual'))
            Mark_Code_fn(row['Codigo'])
        
        if (math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            print('\n {} {} {} {} {}'.format(row['Codigo'],row['Descripcion'],row['TipoProducto'],row['Prefix'], 'AsignacionAuto')) 

        if (not math.isnan(row['Prefix'])) and (math.isnan(row['Codigo'])):
            print('\n {} {} {} {} {}'.format(row['Codigo'],row['Descripcion'],row['TipoProducto'],row['Prefix'], 'AsignacionPrefijo'))         

print('\n Cantidad Codigos Automaticos: ' + str(auto))

Cod1 = str(',').join([str(i) for i in codManuales])

q1 = Queries.MarkingCodes(Cod1,'10203040',False, auto)
cursor= connection.cursor()
cursor.execute(q1)
dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id'])
CodDips = dpcd['id'].tolist()
# %%
q1 = Queries.codObj(7703742071705.0 ,'10203040')
print(q1)
cursor= connection.cursor()
cursor.execute(q1)
CodObj =  pd.DataFrame(data=cursor.fetchall(), columns=ColumnsCode)

# %%
q1 = Queries.codObj(7703742071767.0 ,'10203040')
print(q1)
cursor= connection.cursor()
cursor.execute(q1)
CodObj2 =  pd.DataFrame(data=cursor.fetchall(), columns=ColumnsCode)

#%%
dft = ColumnsDB.dfCodesOK()
# %%
Cod = CodObj.values.tolist()
dft.loc[len(dft.index)] = Cod[0]

# %%
Codigos = [
    {
        "Descripcion": "Producto 6",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
        "Prefix": 77037421776
    },
    {
        "Descripcion": "Producto 7",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
        "Prefix": 77037422010
    },
    {
        "Descripcion": "Producto 6-1",
        "TipoProducto": 1,
        "Brand": "MEDSURE",
        "TargetMarket": "COL",
        "Gpc": "10001695",
        "Url": "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg",
        "State": 3,
        "MeasureUnit": 9,
        "Quantity": 450.0,
        "Prefix": 77037421776
    }]
# %%

pref =[]
pref.append(77037422010)
pref.append(77037421776)
pref.append(77037422010)

Gpref = collections.Counter(pref)

for p,c in Gpref.items():
    print(p,':',c)

# %%
