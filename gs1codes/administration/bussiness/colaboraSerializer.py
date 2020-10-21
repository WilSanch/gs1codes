from rest_framework import serializers 
from administration.models.core import (Enterprise,Country,GpcCategory,MeasureUnit,Code)

class EnterpriseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enterprise 
        fields = [
            'identification',
            'enterprise_name',
            'enterprise_state'
        ]

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields= '__all__'

class GpcCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GpcCategory
        fields= '__all__'

class MeasureUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasureUnit
        fields = '__all__'

class CodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Code
        fields = [
            'id',
            'description',
            'measure_unit',
            'target_market',
            'brand',
            'url',
            'quantity_code',
            'gpc_category',
            'atc_category',
            'textil_category',
            'product_state',
            'measure_unit'
        ]