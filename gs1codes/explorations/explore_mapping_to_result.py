# %%
from explorations import setup_django
# %%
from administration.models.core import ProductType,\
    GpcCategory,\
    MeasureUnit,\
    Country,\
    Enterprise

# %%
Enterprise.objects.select_related('country')\
    .values('id',
            'enterprise_name',
            'country__name')\
    # .get(country_id=152)

# %%
