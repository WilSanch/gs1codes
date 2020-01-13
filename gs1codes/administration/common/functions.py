from administration.common.constants import StateCodes

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
        pref.id,
        sch.description
        from administration_prefix as pref
            inner join administration_schema as sch 
                on sch.id = pref.schema_id
            inner join administration_enterprise as ent
                on pref.enterprise_id = ent.id
        where ent.identification = '{}'
        '''.format(Nit)
        return query