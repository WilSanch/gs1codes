import random
from administration.models.core import Range,Prefix
from django.db import models
from administration.common.constants import StCodes, Ranges

class Queries():
    # def __init__(self):
    #     self.state_codes = StateCodes()
        
    def CodesbyNitbyProductType(Nit,codeState):
        query = '''
        select 
        pt.id as ProductTypeId,
        pt.description as Description,
        count(code.id) as CantGLN
        from administration_code as code
            inner join administration_prefix as pref
                on code.prefix_id = pref.id
            inner join administration_enterprise as ent
                on pref.enterprise_id = ent.id
            left join administration_producttype as pt 
                on pt.id = code.product_type_id  
        where ent.identification = '{}'
            and code.state_id = {}
            and pref.state_id = {}
        group by pt.description,pt.id
        '''.format(Nit, codeState,2)
        return query
    
    def PrefixBySchema(Nit):
        query = '''
        select 
        pref.id_prefix,
        sch.description
        from administration_prefix as pref
            inner join administration_schema as sch 
                on sch.id = pref.schema_id
            inner join administration_enterprise as ent
                on pref.enterprise_id = ent.id
        where ent.identification = '{}'
        '''.format(Nit)
        return query
    
    def AvailableCodes(Nit,Pv):
        '''
        Codigos Disponibles para marcacion segun Nit e indicando
        si se necesita el saldo peso variable o no.
        '''
        operador = ' != ' 
        if (Pv == True):
             operador = ' = '
        
        query='''
        select count(ac.id) from administration_code ac
            inner join administration_prefix ap 
                on  ac.prefix_id = ap.id and ac.range_id = ap.range_id 
            inner join administration_enterprise ae
                on ae.id = ap.enterprise_id 
        where 
        ap.range_id {} {} and
        ap.state_id = {} and
        ac.state_id = {} and
        ae.identification ='{}'
        '''.format(operador,Ranges.Peso_variable.value,StCodes.Asignado.value,StCodes.Disponible.value,Nit)
        return query
    
class Common():
    
    def CalculaDV(Gtin):
        factor=3
        sum=0
        e = len(Gtin)-1
        
        while e>=0:
            sum=sum + int(Gtin[e]) *  factor
            factor = 4-factor
            e=e-1

        dv=(1000 - sum) % 10
        GTIN_CDV = Gtin + str(dv)
        return GTIN_CDV
    
    def PrefixGenerator(range_code):
        '''
        Genera un prefijo aleatorio basandose en el rango recibido 
        y excluyendolo de los prefijos asignados en la base de datos
        '''
        model_range:Range = Range.objects.get(id=range_code)
        
        if str(model_range.initial_value)[0:3]=='770':
            intial = int(str(model_range.initial_value))
            final = int(str(model_range.final_value))
        else:
            intial = int(str(model_range.country_code) + str(model_range.initial_value))
            final = int(str(model_range.country_code) + str(model_range.final_value))
                
        all_prefix_list = range(intial,final)        
        assigned_prefix_list = Prefix.objects.values_list('id_prefix', flat=True).filter(range_id=range_code)
    
        available_prefix_list = list(set(all_prefix_list)-set(assigned_prefix_list))
        
        prefix=random.sample(available_prefix_list, 1) 
    
        return prefix[0]
    
    def CodeGenerator(prefix, range_id):
        
        cat:Range = Range.objects.get(id=range_id)

        quantity_code=cat.quantity_code
        ceros= len(str(quantity_code))-1

        listCodes =[]

        for c in range(quantity_code):
            
            if ceros>0:
                csdv = str(prefix) + str(c).zfill(ceros)
            else:
                csdv = str(prefix)
            
            ccdv = Common.CalculaDV(csdv)
            listCodes.append(ccdv)
            
        return listCodes
