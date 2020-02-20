from django.db import models

class Code(models.Model):
   
    alternate_code = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, null=False)
    assignment_date = models.DateTimeField(null=False)
    url = models.CharField(max_length=500, blank=True, null=True)
    quantity_code = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
    gln_name = models.CharField(max_length=100,blank=True, null=True)
    agreement_id =  models.BigIntegerField(null=True)
    atc_category_id = models.BigIntegerField(null=True)
    brand_id =  models.BigIntegerField(null=False)
    gpc_category_id = models.BigIntegerField(null=True)
    measure_unit_id =  models.BigIntegerField(null=True)
    prefix_id = models.BigIntegerField(null=False)
    product_state_id = models.BigIntegerField(null=False)
    product_type_id = models.BigIntegerField(null=False)
    range_id = models.BigIntegerField(null=False)
    state_id = models.BigIntegerField(null=False)
    target_market_id = models.BigIntegerField(null=True)
    textil_category_id = models.BigIntegerField(null=True)
    
    class Meta:
        managed = False
        app_label = 'temp'