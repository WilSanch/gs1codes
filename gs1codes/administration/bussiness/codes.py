import json
import math
import pandas as pd
import collections
from rest_framework import serializers
from administration.models.core import ProductType,GpcCategory,MeasureUnit
from administration.common.functions import Queries, Common
from administration.bussiness.models import *
from administration.common.constants import *
from colorama import Fore, Back, Style
from django.db import connection, transaction

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
      
    CodiVal = valida_codes(marcation["Codigos"])
    
    codigosRepetidos = codigosRepetidosfn(CodiVal)
    
    if(len(codigosRepetidos)>=1):
          return {
                "IdCodigos": codigosRepetidos,
                "MensajeUI": marcation["Nit"],
                "Respuesta": 'Error Codigos Repetidos'
                }
    
    TotalMark = TotalMarkCodes(CodiVal)
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
    
    dfcodesMark = pd.DataFrame(data=CodiVal)
    dfcodesMark[['Codigo','Prefix']]=dfcodesMark[['Codigo','Prefix']].astype(float)
    dfcodesMarkGroup = dfcodesMark.groupby('TipoProducto')
    
    prb = Mark_Codes_fn(dfcodesMarkGroup, marcation['Nit'])

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
    pv=0
    
    for c in codigos:
        if(c['TipoProducto'] == ProductType.Producto_peso_variable.value):
            pv=pv+1
    
    if pv>0 : 
        markCodeGroupbyType.TotalVariableWeight = dfcodesMarkGroup.get_group(ProductType.Producto_peso_variable.value)['Descripcion'].count()
    else:
        markCodeGroupbyType.TotalVariableWeight = 0
        
    markCodeGroupbyType.TotalCodesMark = len(codigos)   
    markCodeGroupbyType.TotalNonVariableWeight = markCodeGroupbyType.TotalCodesMark - markCodeGroupbyType.TotalVariableWeight
    return markCodeGroupbyType
 
def TotalAviablesCodes(Nit, VariableWeight):
    q1 = Queries.AvailableCodes(Nit, VariableWeight)
    cursor= connection.cursor()
    cursor.execute(q1)
    spv = cursor.fetchone()
    return spv[0]

def Mark_Code_fn(Code, Nit):
    q1 = Queries.codObj(Code ,Nit)
    cursor= connection.cursor()
    cursor.execute(q1)
    CodObj =  dfCodesOK(data=cursor.fetchall())

    if (CodObj['state_id'].tolist()[0] != StCodes.Disponible.value) and \
       (CodObj['state_id'].tolist()[0] != StCodes.Reservado_Migración.value):
        print('Asignado')
    else:
        print('Disponible')  
    
def Mark_Codes_fn(dfg, Nit):
    
    for TipoProducto, Codigo in dfg:
        rc = MarkedCodesfn(Codigo, Nit, TipoProducto)
        for row_index, row in Codigo.iterrows():
            if (not math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
                #AsignacionManual
                Code = rc.Manual.pop()
                print(Code,' Manual')
            
            if (math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
                #AsignacionAuto
                Code = rc.Auto.pop()
                print(Code, ' Auto')

            if (not math.isnan(row['Prefix'])) and (math.isnan(row['Codigo'])):
                # AsignacionPrefijo
                pr = row['Prefix']
                for prefix in rc.Prefix:
                    prc=prefix['Prefix']
                    if prc == pr:
                        Code = prefix['Codes'].pop()
                        print(Code,' Prefijo:' , pr)
            
def MarkedCodesfn(df, Nit, TipoProducto):
    rc = RequestCodes
    rc.Auto=[]
    rc.Manual=[]
    rc.Prefix=[]
    auto = 0
    codManuales = []
    CodAuto = []
    Prefix = []
    codPref=[]
    strPref=''
    for row_index, row in df.iterrows():
        if (not math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            codManuales.append(row['Codigo'])
                
        if (math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            auto = auto + 1
            
        if (not math.isnan(row['Prefix'])) and (math.isnan(row['Codigo'])):
            Prefix.append(row['Prefix'])
    
    CodManual = str(',').join([str(i) for i in codManuales])    
    prefixGrouped = collections.Counter(Prefix)
    
    pv = False
    if (TipoProducto == ProductType.Producto_peso_variable.value):
        pv = True
    
    if (len(codManuales)>0) :
        q1 = Queries.MarkingCodesManual(CodManual,Nit,pv, auto)
        cursor= connection.cursor()
        cursor.execute(q1)
        dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id'])
        CodDips = dpcd['id'].tolist() 
        rc.Manual = codManuales
        rc.Auto = CodDips
     
    if (len(Prefix)>0):
        for p,c in prefixGrouped.items():
            print(p,':',c)    
            q1 = Queries.MarkingCodesPrefix(Nit,pv,CodManual,p,c)
            cursor= connection.cursor()
            cursor.execute(q1)
            dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id'])
            CodDips = dpcd['id'].tolist()
            rc.Prefix.append({
                "Prefix":p,
                "Codes":CodDips})
            codPref.append(CodDips)
        strPref = str(',').join([str(i) for i in codPref])
            
    if (auto > 0):
        q1 = Queries.MarkingCodesAuto(Nit,pv, strPref.replace('[','').replace(']',''), CodManual, auto)
        cursor= connection.cursor()
        cursor.execute(q1)
        dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id'])
        CodDips = dpcd['id'].tolist()
        rc.Auto = CodDips
    
    return rc         

def valida_ver(code : MarkedCode):
      
      if('Gpc' not in code):
            code['Gpc'] = None
            
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
        
def valida_codes(codes):
    for code in codes:
        if('Codigo' not in code):
            code['Codigo'] = None
            
        if('Prefix' not in code):
            code['Prefix'] = None
        
        if('Descripcion' not in code):
            code['Descripcion'] = None
        
        if('TipoProducto' not in code):
            code['TipoProducto'] = None
        
        if('Brand' not in code):
            code['Brand'] = None
        
        if('TargetMarket' not in code):
            code['TargetMarket'] = None
        
        if('Gpc' not in code):
            code['Gpc'] = None
        
        if('Atc' not in code):
            code['Atc'] = None
        
        if('Url' not in code):
            code['Url'] = None
        
        if('State' not in code):
            code['State'] = ProducState.En_Desarrollo.value
        
        if('MeasureUnit' not in code):
            code['MeasureUnit'] = None
        
        if('Quantity' not in code):
            code['Quantity'] = None
        
    return codes