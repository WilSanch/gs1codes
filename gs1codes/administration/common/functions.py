import random
from administration.models.core import Range,Prefix,Code
from django.db import models, connection
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
    
    def MarkingCodesManual(Codes,Nit,PV, CantAuto):
        
        operador = '!=' 
        if (PV == True):
             operador = '='
             
        query='''
        SELECT Code.id
        FROM administration_code AS Code
            INNER JOIN administration_prefix AS Pref
                ON Code.prefix_id = Pref.id
            INNER JOIN administration_enterprise AS Ent
                ON Pref.enterprise_id = Ent.id
        WHERE Code.id NOT IN ( {} )
            AND Ent.identification = '{}'
            AND Pref.state_id = {}
            AND Code.state_id = {}
            AND Pref.range_id {} 12
        LIMIT {}
        '''.format(Codes, Nit, StCodes.Asignado.value, StCodes.Disponible.value, operador, CantAuto)
        return query
    
    def MarkingCodesAuto(Nit,PV, CodPref, CodManual, CantAuto):
        
        codesManual = ' '
        if len(CodManual)>0:
           codesManual= ' AND Code.id NOT IN ({})'.format(CodManual)  
        
        codesPref = ' '
        if len(CodPref)>0:
           codesPref= ' AND Code.id NOT IN ({})'.format(CodPref)  
        
        operador = '!=' 
        if (PV == True):
             operador = '='
             
        query='''
        SELECT Code.id
        FROM administration_code AS Code
            INNER JOIN administration_prefix AS Pref
                ON Code.prefix_id = Pref.id
            INNER JOIN administration_enterprise AS Ent
                ON Pref.enterprise_id = Ent.id
        WHERE Ent.identification = '{}'
            AND Pref.state_id = {}
            AND Code.state_id = {}
            AND Pref.range_id {} 12
            {}
            {}
        LIMIT {}
        '''.format(Nit, StCodes.Asignado.value, StCodes.Disponible.value, operador, codesManual, codesPref, CantAuto)
        return query
    
    def MarkingCodesPrefix(Nit,PV,codManuales,Prefix,Cant):
        
        codes =' '
        if len(codManuales)>0:
           codes= ' AND Code.id NOT IN ({})'.format(codManuales) 
        
        operador = '!=' 
        if (PV == True):
             operador = '='
             
        query='''
        SELECT Code.id
        FROM administration_code AS Code
            INNER JOIN administration_prefix AS Pref
                ON Code.prefix_id = Pref.id
            INNER JOIN administration_enterprise AS Ent
                ON Pref.enterprise_id = Ent.id
        WHERE Ent.identification = '{}'
            AND Pref.state_id = {}
            AND Code.state_id = {}
            AND Pref.range_id {} 12
            AND Pref.id_prefix = {}
            {}
        LIMIT {}
        '''.format(Nit, StCodes.Asignado.value, StCodes.Disponible.value, operador, Prefix,codes,Cant)
        return query
    
    def codObj(Nit,Code):
        query='''
        SELECT 
		Code.id ,
        alternate_code ,
        description ,
        Code.assignment_date ,
        url ,
        quantity_code ,
        gln_name ,
        agreement_id ,
        atc_category_id ,
        brand_id,
        gpc_category_id,
        measure_unit_id ,
        Code.prefix_id ,
        product_state_id,
        product_type_id ,
        Code.range_id ,
        Code.state_id ,
        target_market_id ,
        textil_category_id 
        FROM administration_code AS Code
            INNER JOIN administration_prefix AS Pref
                ON Code.prefix_id = Pref.id
            INNER JOIN administration_enterprise AS Ent
                ON Pref.enterprise_id = Ent.id
        WHERE Code.id = {}
            AND Ent.identification = '{}'
        '''.format(Nit, Code)
        return query
    
    def createCodeTemp():
        query='''
            CREATE TEMPORARY TABLE IF NOT EXISTS temp_code (
                id BIGINT,
                alternate_code BIGINT,
                description VARCHAR(200),
                assignment_date TIMESTAMP,
                url VARCHAR(500),
                quantity_code DECIMAL,
                gln_name VARCHAR(100),
                agreement_id INT,
                atc_category_id INT,
                brand_id INT,
                gpc_category_id INT,
                measure_unit_id INT,
                prefix_id INT,
                product_state_id INT,
                product_type_id INT,
                range_id INT,
                state_id INT,
                target_market_id INT,
                textil_category_id INT)
        '''
        return query

    def upserCode():
        query='''
            insert into administration_code
                (
                id,
                alternate_code,
                description,
                assignment_date,
                url,
                quantity_code,
                gln_name,
                agreement_id,
                atc_category_id,
                brand_id,
                gpc_category_id,
                measure_unit_id,
                prefix_id,
                product_state_id,
                product_type_id,
                range_id,
                state_id,
                target_market_id,
                textil_category_id
                )
            select
                tc.id,
                tc.alternate_code,
                tc.description,
                tc.assignment_date,
                tc.url,
                tc.quantity_code,
                tc.gln_name,
                tc.agreement_id,
                tc.atc_category_id,
                tc.brand_id,
                tc.gpc_category_id,
                tc.measure_unit_id,
                tc.prefix_id,
                tc.product_state_id,
                tc.product_type_id,
                tc.range_id,
                tc.state_id,
                tc.target_market_id,
                tc.textil_category_id
            from temp_code as tc
            on conflict (id) do update 
            set description = EXCLUDED.description,
           		assignment_date= EXCLUDED.assignment_date,
           		url=EXCLUDED.url,
           		quantity_code= EXCLUDED.quantity_code,
           		gln_name=EXCLUDED.gln_name,
				agreement_id=EXCLUDED.agreement_id,
				atc_category_id=EXCLUDED.atc_category_id,
				brand_id=EXCLUDED.brand_id,
				gpc_category_id=EXCLUDED.gpc_category_id,
				measure_unit_id=EXCLUDED.measure_unit_id,
				prefix_id=EXCLUDED.prefix_id,
				product_state_id=EXCLUDED.product_state_id,
				product_type_id=EXCLUDED.product_type_id,
				range_id=EXCLUDED.range_id,
				state_id=EXCLUDED.state_id,
				target_market_id=EXCLUDED.target_market_id,
				textil_category_id=EXCLUDED.textil_category_id;
        '''
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
    
    def CodeGenerator(prefix, range_id, quantity=0):
        
        cat:Range = Range.objects.get(id=range_id)
        obj_prefix = Prefix.objects.get(id_prefix=prefix)
        prefix_code = obj_prefix.id

        if (quantity==0):
            quantity_code=cat.quantity_code
        else:
            quantity_code= quantity

        ceros= len(str(quantity_code))-1

        all_code_list = []

        for i in range(cat.quantity_code):
            if ceros>0:
                csdv = str(prefix) + str(i).zfill(ceros)
            else:
                csdv = str(prefix) + str(i)
            
            ccdv = Common.CalculaDV(csdv)
            all_code_list.append(int(ccdv))

        code_list = Code.objects.filter(prefix_id=prefix_code).values_list('id', flat=True)

        if (not code_list):
            result = random.sample(all_code_list, quantity)
        else:
            available_code_list = list(set(all_code_list)-set(code_list))
            result = random.sample(available_code_list, quantity)
        
        return result

    def GetAvailablePrefix(required_quantity):
        query='''
        select id, min(available_quantity) as available_quantity 
        from 
        (
            select C.quantity_code - Count(B.id) as available_quantity, A.id
            From administration_prefix A
            left join administration_code B on A.id = B.prefix_id 
            inner join administration_range C on A.range_id = C.id 
            group by  A.id, C.quantity_code
        ) a
        where available_quantity >= {}
        group by id
        
        '''.format(required_quantity)

        cursor= connection.cursor()
        cursor.execute(query)
        spv = cursor.fetchone()
        
        return spv[0]