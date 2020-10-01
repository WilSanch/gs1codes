import random
from administration.models.core import Range,Prefix,Code
from django.db import models, connection
from administration.common.constants import StCodes, Ranges
from datetime import datetime

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

    def upsertCode():
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
    

    def PrefixToCreateFromRegroup(prefix_id,range_id):
        query = '''
                select Substring(CAST(ID AS Varchar(20)), 1, 11) As id, 
                        Max(case when assignment_date != null then assignment_date else null end) as assignment_date, 
                        Max(case when state_id = 2 or state_id = 9 then 1 else 0 end) As assigned
                from administration_code ac 
                where prefix_id = {} and range_id = {}
                group by Substring(CAST(ID AS Varchar(20)), 1, 11) 
            '''.format(prefix_id, range_id)
        return query

    def CodeRegroupUpdate(prefix_array,range_id):
        query = '''
                update administration_code 
                set prefix_id = b.id,
                    range_id = {}
                from administration_code a 
                inner join 
                (
                    select  a.id, id_prefix
                    from administration_prefix a
                    inner join 
                    (
                        select unnest(array{}) as id
                    ) b on a.id_prefix = cast(b.id as bigint) and a.range_id = {}
                ) b on Substring(CAST(a.id AS Varchar(20)), 1, 11) = cast(b.id_prefix as varchar(13))
                '''.format(range_id,prefix_array,range_id)
        return query

    def CodeRegroupDelete(prefix_array,range_id):
        query = '''
                with codes as 
                    (
                        select  cast(b.id as varchar(13)) as id_prefix
                        from administration_prefix a
                        inner join 
                        (
                            select unnest(array{}) as id
                        ) b on a.id_prefix = cast(b.id as bigint) and a.range_id = {} and state_id = 12
                    )
                delete from administration_code a 
                using codes b
                where Substring(CAST(a.id AS Varchar(20)), 1, 11) = b.id_prefix and state_id = 1
                '''.format(prefix_array,range_id)
        return query

    
    def validateGtin14(GTIN14_SINESQUEMA,idEnterprise):
        q1 = '''
            SELECT COUNT(ID) as Cant
            FROM administration_prefix ap 
            WHERE ap.id =
            (
                SELECT prefix_id FROM administration_code ac WHERE ID = '{}'
            )
            AND ap.enterprise_id = {};
        '''.format(GTIN14_SINESQUEMA,idEnterprise)
        return q1
    
    def GetGtin14byGtin13(Gtin13):
        q1 = '''
        SELECT 
            ID,
            ID_CODE_id,
            QUANTITY
        FROM administration_code_gtin14 acg 
        WHERE ID_CODE_id = '{}';
        '''.format(Gtin13)
        return q1
    
    def GetGetin14s(Gtin13):
        q1 = '''
        SELECT 
            ID,
            ID_CODE_id,
            DESCRIPTION,
            QUANTITY
        FROM administration_code_gtin14 acg 
        WHERE ID_CODE_id = '{}';
        '''.format(Gtin13)
        return q1
    
    def GetGetin14sList(Gtin13s):
        q1 = '''
        SELECT 
            ID,
            ID_CODE_id,
            DESCRIPTION,
            QUANTITY
        FROM administration_code_gtin14 acg 
        WHERE ID_CODE_id in ({})
        ORDER BY 2;
        '''.format(Gtin13s)
        return q1
    
    def getGtinbyNit(Nit):
        q1='''
        select 
            g14.id,
            g14.description,
            g14.quantity,
            g14.id_code_id,
            st.description as state
        from administration_code_gtin14 as g14
            inner join administration_code as code
                on g14.id_code_id = code.id 
            inner join administration_prefix as pref
                on code.prefix_id = pref.id
            inner join administration_enterprise as ent 
                on pref.enterprise_id = ent.id 
            inner join administration_state as st
                on st.id = g14.state_id 
        where ent.identification ='{}'
        '''.format(Nit)
        return q1

    def getPrefixesByEnterprise(id):
        q1='''
            select distinct A.id_prefix, C.quantity_code, C.name as type, D.description as schema, B.description as state, 
                    A.observation, coalesce(to_char(A.assignment_date, 'DD/MM/YYYY'), '') as assignment_date, 
                    coalesce(to_char(A.validity_date, 'DD/MM/YYYY'), '') as validity_date, count(E.id) as assigned,
                    C.quantity_code - count(E.id) as available, A.id, A.state_id, 
                    case when C.regrouping = true then 1 else 0 end as regrouping 
            From administration_prefix A
            inner join administration_state B on A.state_id = B.id
            inner join administration_range C on A.range_id = C.id 
            inner join administration_schema D on A.schema_id = D.id
            left join administration_code  E on A.id = E.prefix_id  
            where A.enterprise_id = {}
            group by A.id_prefix, C.quantity_code, C.name, D.description, B.description, 
                    A.observation, A.assignment_date, A.validity_date,C.quantity_code,
                    A.id, A.state_id, C.regrouping 
            order by A.id_prefix 
        '''.format(id)
    
        return q1

    def getPrefixesByEnterpriseActive(id):
        q1='''
            select distinct A.id_prefix, C.quantity_code, C.name as type, D.description as schema, B.description as state, 
                    A.observation, coalesce(to_char(A.assignment_date, 'DD/MM/YYYY'), '') as assignment_date, 
                    coalesce(to_char(A.validity_date, 'DD/MM/YYYY'), '') as validity_date, count(E.id) as assigned,
                    C.quantity_code - count(E.id) as available, A.id, A.state_id, 
                    case when C.regrouping = true then 1 else 0 end as regrouping 
            From administration_prefix A
            inner join administration_state B on A.state_id = B.id
            inner join administration_range C on A.range_id = C.id 
            inner join administration_schema D on A.schema_id = D.id
            left join administration_code  E on A.id = E.prefix_id  
            where A.enterprise_id = {} and A.state_id = 2
            group by A.id_prefix, C.quantity_code, C.name, D.description, B.description, 
                    A.observation, A.assignment_date, A.validity_date,C.quantity_code,
                    A.id, A.state_id, C.regrouping 
            order by A.id_prefix 
        '''.format(id)
    
        return q1
    

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
            intial = int(str(model_range.country_code) + str(model_range.initial_value).zfill(len(str(model_range.final_value))))
            final = int(str(model_range.country_code) + str(model_range.final_value))
                
        all_prefix_list = range(intial,final)        
        assigned_prefix_list = Prefix.objects.values_list('id_prefix', flat=True).filter(range_id=range_code)
    
        available_prefix_list = list(set(all_prefix_list)-set(assigned_prefix_list))
        
        prefix=random.sample(available_prefix_list, 1) 
    
        return prefix[0]
    
    def CodeGenerator(prefix, range_id, quantity=0):
        if (not prefix):
            return list()

        cat:Range = Range.objects.get(id=range_id)
        obj_prefix = Prefix.objects.get(id_prefix=prefix)
        prefix_code = obj_prefix.id

        if (quantity==0):
            quantity_code=cat.quantity_code
        else:
            quantity_code= quantity

        ceros= len(str(cat.quantity_code))-1

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

    def GetAvailablePrefix(required_quantity,enterprise_id,prefix_id):
        if (prefix_id == 0 or prefix_id == None):
            query='''
            select id, min(available_quantity) as available_quantity, enterprise_id 
            from 
            (
                select C.quantity_code - Count(B.id) as available_quantity, A.id, A.state_id, A.enterprise_id
                From administration_prefix A
                left join administration_code B on A.id = B.prefix_id 
                inner join administration_range C on A.range_id = C.id 
                group by  A.id, C.quantity_code, A.enterprise_id
            ) a
            where available_quantity >= {} and enterprise_id = {} and state_id = 2
            group by id, enterprise_id 
            
            '''.format(required_quantity,enterprise_id)
        else:
            query='''
            select id, min(available_quantity) as available_quantity, enterprise_id, range_id
            from 
            (
                select C.quantity_code - Count(B.id) as available_quantity, A.id, A.state_id, A.enterprise_id, C.id as range_id 
                From administration_prefix A
                left join administration_code B on A.id = B.prefix_id 
                inner join administration_range C on A.range_id = C.id 
                group by  A.id, C.quantity_code, A.enterprise_id, C.id
            ) a
            where available_quantity >= {} and enterprise_id = {} and state_id = 2 and range_id = {}
            group by id, enterprise_id, range_id
            
            '''.format(required_quantity,enterprise_id,prefix_id)

        cursor= connection.cursor()
        cursor.execute(query)
        spv = cursor.fetchone()
        
        if (spv == None):
            return None
        else:
            return spv[0]

    def GetIdAvailablePrefix(enterprise_id,range_id):
        query='''
        select id, code_residue as available_quantity, enterprise_id 
        From administration_prefix 
        where enterprise_id = {} and range_id = {} and code_residue > 0 and state_id = 2  
        
        '''.format(enterprise_id,range_id)

        cursor= connection.cursor()
        cursor.execute(query)
        spv = cursor.fetchone()
        
        if (spv == None):
            return None
        else:
            return spv[0]
    
    def addYears(date_to_add: datetime, years):
        try:
        #Devuelve el mismo dia del año correspondiente
            return date_to_add.replace(year = date_to_add.year + years)
        except ValueError:
        #Si no es el mismo día, retornará otro, es decir, del 29 de febrero al 1 de marzo, etc.
            return date_to_add + (date(date_to_add.year + years, 1, 1) - date(date_to_add.year, 1, 1))