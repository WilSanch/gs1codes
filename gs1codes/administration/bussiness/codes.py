import json
import pandas as pd
from rest_framework import serializers
from administration.models.core import ProductType,GpcCategory,MeasureUnit
from administration.common.functions import Queries, Common
from administration.bussiness.models import *
from colorama import Fore, Back, Style

class ProductTypeSerializer(serializers.ModelSerializer): 
  class Meta: 
    model = ProductType 
    fields = '__all__'

class GpcCategorySerializer(serializers.ModelSerializer): 
  class Meta: 
    model = GpcCategory 
    # fields = ['brick_code','spanish_name_brick']
    fields = '__all__'
    
class MeasureUnitsSerializer(serializers.ModelSerializer): 
  class Meta: 
    model = MeasureUnit 
    # fields = ['brick_code','spanish_name_brick']
    fields = '__all__'

def get_gpc_category(marcation: MarkData):
    gpc =  GpcCategory.objects.all()     
    data = {"result": list(gpc.values("id", "spanish_name_brick"))}        
    return data
    
def mark_codes(marcation: MarkData):
    
    codigosRepetidos = codigosRepetidosfn(marcation["Codigos"])
    if(len(codigosRepetidos)>=1):
          return {
                "IdCodigos": codigosRepetidos,
                "MensajeUI": marcation["Nit"],
                "Respuesta": 'Error Codigos Repetidos'
                }
          
    jsonPrb = []
    for code in marcation["Codigos"]:
      jsonPrb.append({
      "Cod":code['Codigo'],
      "Msj":valida_ver(code)})     
      
    return {
        "IdCodigos": jsonPrb, #list(marcation["Codigos"]),
        "MensajeUI": marcation["Nit"],
        "Respuesta": 100
    }  

def codigosRepetidosfn(codigos):  
    df = pd.DataFrame(data=codigos)
    rep = df.groupby(['Codigo']).count()
    repetidos = rep[rep.Descripcion==2]
    msgs = "El código " + repetidos.index.astype("str") + " tiene " + repetidos.Descripcion.astype("str") + " repeticiones"
    return msgs.to_list()

def valida_ver(code : MarkedCode):
      
      if('Gpc' not in code):
            code['Gpc'] = None
            print(Fore.RED + 'Gpc Vacio: ' + str(code['Codigo']))
            print(Style.RESET_ALL)
            
      if('MeasureUnit' not in code):
            code['MeasureUnit'] = None
            print('MeasureUnit Vacio: ' + str(code['Codigo']))
            
      mu = MeasureUnit.objects.filter(id= code['MeasureUnit']).count()
      if (mu>0):
            gpc = GpcCategory.objects.filter(brick_code= code['Gpc']).count()    
            if (gpc>0 ):
              return True
            else:
              return 'No existe categoria GPC'
      else:
            return 'No existe unidad de medida'