# %%
%load_ext autoreload
%autoreload 2

# %%
# from explorations import setup_django
import sys
import os
import django
sys.path.extend([os.path.dirname(os.getcwd())])
django.setup()
#%%
from administration.common.functions import Common, Queries
from django.db import connection
import pandas as pd
from administration.models.core import ProductType,\
    GpcCategory,\
    MeasureUnit,\
    Country,\
    Enterprise,\
    Code,\
    Enterprise,\
    Prefix,\
    Schema,\
    ProductType,\
    Range

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
from administration.common.constants import StateCodes
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
ProductType.objects.all()

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

#%%
from administration.common.functions import Queries,Common

# %%
%%time
r=2
pref = Common.PrefixGenerator(r)
cat:Range = Range.objects.get(id=r)

x=cat.quantity_code
y= len(str(x))-1

display(pref)

list =[]

for c in range(x):
    csdv = str(pref) + str(c).zfill(y)
    ccdv = Common.CalculaDV(csdv)
    list.append(ccdv)
    

# %%
