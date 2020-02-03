from django.db import transaction
import json
import pandas as pd
from rest_framework import serializers
from administration.models.core import ProductType,GpcCategory,MeasureUnit,Prefix,Range,Code
from administration.common.functions import Queries, Common
from administration.common.constants import ProductType, StateCodes
from administration.bussiness.models import *
from datetime import datetime

# from colorama import Fore, Back, Style

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
            # print(Fore.RED + 'Gpc Vacio: ' + str(code['Codigo']))
            # print(Style.RESET_ALL)
            print('')
            
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

def code_assignment(prefix: Prefix, ac: CodeAssignmentRequest, username: str, range_prefix: Range):
  try:
    
    product_type: int = None
    code_list = Common.CodeGenerator(prefix.id_prefix, prefix.range_id)
    bulk_code=[]

    if (ac.Type == CodeType.CodigoGtin8Nuevos):
      product_type = ProductType.Producto

    if (ac.Type == CodeType.DerechoIdentificacionGln):
      product_type = ProductType.Gln

    if (ac.Type == CodeType.IdentificacionDocumentos):
      product_type = ProductType.Recaudo



    for code in code_list:
      new_code= Code()

      new_code.id = code
      new_code.assignment_date = datetime.now()
      new_code.prefix_id = prefix.id
      new_code.state_id = StateCodes.Asignado
      new_code.product_type_id = product_type

      bulk_code.append(new_code)
    
    with transaction.atomic():
      Code.objects.bulk_create(bulk_code)

    return ""

  except IntegrityError:
    return "No fue posible insertar los códigos."

