from django.db import transaction
import json
import pandas as pd
from rest_framework import serializers
from administration.models.core import ProductType,GpcCategory,MeasureUnit,Prefix,Range,Code
from administration.common.functions import Queries, Common
from administration.common.constants import ProductTypeCodes, StCodes
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
    
    jsonPrb = []
      
    codigosRepetidos = codigosRepetidosfn(marcation["Codigos"])
    
    if(len(codigosRepetidos)>=1):
          return {
                "IdCodigos": codigosRepetidos,
                "MensajeUI": marcation["Nit"],
                "Respuesta": 'Error Codigos Repetidos'
                }
    
    TotalMark = TotalMarkCodes(marcation['Codigos'])
    AvailableCodesVariableWeight = TotalAviablesCodes(marcation["Nit"],True)
    AvailableCodesNoneVariableWeight = TotalAviablesCodes(marcation["Nit"],False)
    
    if (TotalMark.TotalVariableWeight > AvailableCodesVariableWeight):
         return {
                "IdCodigos": jsonPrb,
                "MensajeUI": 'Error Saldos',
                "Respuesta": 'Esta tratando de marcar {} codigos de pesovariable y dispone de {}'.format(TotalMark.TotalVariableWeight,AvailableCodesVariableWeight)
                }       
         
    if (TotalMark.TotalNonVariableWeight > AvailableCodesNoneVariableWeight):
         return {
                "IdCodigos": jsonPrb,
                "MensajeUI": 'Error Saldos',
                "Respuesta": 'Esta tratando de marcar {} codigos y dispone de {}'.format(TotalMark.TotalNonVariableWeight,AvailableCodesNoneVariableWeight)
                }       
    
    dfcodesMark = pd.DataFrame(data=marcation['Codigos'])
    dfcodesMarkGroup = dfcodesMark.groupby('TipoProducto')
    
    # Agrupacion pot Tipo de Producto
    for TipoProducto, Codigo in dfcodesMarkGroup:
        sal = Prbfn(Codigo,TipoProducto) 
        
    for code in marcation["Codigos"]:
      jsonPrb.append({
      "Cod":code['Descripcion'],
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

def TotalMarkCodes(codigos):
    dfcodesMark = pd.DataFrame(data=codigos)
    dfcodesMarkGroup = dfcodesMark.groupby('TipoProducto') 
    
    markCodeGroupbyType = MarkCodeGroupbyType 
    markCodeGroupbyType.TotalVariableWeight =dfcodesMarkGroup.get_group(ProductType.Producto_peso_variable.value)['Codigo'].count()
    markCodeGroupbyType.TotalCodesMark = len(codigos)   
    markCodeGroupbyType.TotalNonVariableWeight = markCodeGroupbyType.TotalCodesMark - markCodeGroupbyType.TotalVariableWeight
    
    return markCodeGroupbyType
  
def TotalAviablesCodes(Nit, VariableWeight):
    q1 = Queries.AvailableCodes(Nit, VariableWeight)
    cursor= connection.cursor()
    cursor.execute(q1)
    spv = cursor.fetchone()
    return spv[0]
 
def Prbfn(df,tp):
      
    for row_index, row in df.iterrows():
        print('\n {} {} {}'.format(row['Codigo'],row['Descripcion'],row['TipoProducto']))
        valida_ver(row)
    

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
      product_type = ProductType.Producto.value

    if (ac.Type == CodeType.DerechoIdentificacionGln):
      product_type = ProductType.GLN.value

    if (ac.Type == CodeType.IdentificacionDocumentos):
      product_type = ProductType.Recaudo.value



    for code in code_list:
      new_code= Code()

      new_code.id = code
      new_code.assignment_date = datetime.now()
      new_code.prefix_id = prefix.id
      new_code.state_id = StCodes.Asignado.value
      new_code.product_type_id = product_type

      bulk_code.append(new_code)
    
    with transaction.atomic():
      Code.objects.bulk_create(bulk_code)

    return ""

  except IntegrityError:
    return "No fue posible insertar los códigos."

