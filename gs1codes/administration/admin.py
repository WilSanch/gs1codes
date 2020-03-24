from django.contrib import admin
from django.contrib.admin import ModelAdmin, register
from administration.models import ProductType, Brand, Code, User
# Register your models here.

@register(ProductType)
class ptAdmin(ModelAdmin):
    list_display = ('description','state')
    
@register(Brand)
class ptBrand(ModelAdmin):
    list_display = ('id','name')
    
@register(Code)
class ptCode(ModelAdmin):
    list_display = ('id','description')
    
@register(User)
class ptUser(ModelAdmin):
    list_display = ('id','email')
    