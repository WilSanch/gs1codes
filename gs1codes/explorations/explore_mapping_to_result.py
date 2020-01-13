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
# %%
from django.db import connection
from administration.common.functions import Queries
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
for code in Code.objects.raw(
'''
select 
ent.identification,
ent.enterprise_name,
code.id,
pref.id as prefi
from administration_code as code
	inner join administration_prefix as pref
		on code.prefix_id = pref.id
	inner join administration_enterprise as ent
		on pref.enterprise_id = ent.id limit 10
''',):
    print(code.id,code.enterprise_name,code.prefi)

# %%
p=Code.objects.raw(
'''
select 
ent.identification,
ent.enterprise_name,
code.id,
pref.id as prefi
from administration_code as code
	inner join administration_prefix as pref
		on code.prefix_id = pref.id
	inner join administration_enterprise as ent
		on pref.enterprise_id = ent.id limit 10
''')

# %%
ent = Enterprise.objects.select_related('prefix',)\
.values('id','prefix','prefix__range_id')
print(ent.query)


# %%
from administration.common.constants import StateCodes

q1= Queries.CodesbyNitbyProductType('10203040', StateCodes().Disponible)
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
