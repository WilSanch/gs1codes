from typing import TypedDict, List
import datetime
from datetime import datetime, date
import json
from administration.models.core import Prefix,Schema,Enterprise,CodeTypeByRanges,CodeTypeBySchemas, Range  
from administration.bussiness.models import PrefixId, ActivationInactivationBM, MarkCodeRespose, CodeAssignmentRequest, CodeAssignation
from datetime import datetime
from django.db import connection,transaction, IntegrityError
from administration.models.core import Prefix,Schema,Enterprise,CodeTypeBySchemas,Range,Code
from administration.bussiness.models import *
from administration.bussiness.enterprise import new_enterprise, update_totals_enterprise
from administration.bussiness.codes import code_assignment
from administration.common.constants import UserMessages, PrefixRangeType, CodeType, StCodes
from administration.common.functions import Common,Queries
import pandas as pd

def update_validity_date_prefix(model: Prefix):
    schema:Schema = Schema.objects.filter(id=model.schema_id).first()
    if (not schema):
        return False
    else:
        if (schema.validity_date == None):
            if (schema.validate_from_creation_date == False):
                model.validity_date = Common.AddYears(model.assignment_date, schema.validity_time)
        else:
            model.validity_date = schema.validity_date
    return model.validity_date

def prefix_activation(model: Prefix, assignment_date, observation, user):
    try:
        if (model.state_id == StCodes.No_Reutilizable.value):
            return "No puede activar un prefijo cuyo estado es NO REUTILIZABLE"
        else:
            model.state_id = StCodes.Asignado.value
            model.assignment_date = assignment_date
            model.observation = "ACTIVACIÓN MANUAL: " + observation
            model.validity_date = update_validity_date_prefix(model)  
            model.save()
        return ""

    except model.DoesNotExist:
        return "El prefijo no existe"

def get_id7700_from_id29(id_prefix):
    return int("7700" + str(id_prefix)[2:])

def prefix_inactivation(model: Prefix, modification_date, observation, user):
    try:
        if (str(model.id_prefix).startswith("29")): 
            prefix_to_inactivate: Prefix = Prefix.objects.get(id_prefix=get_id7700_from_id29(model.id_prefix))
            prefix_to_inactivate.state_id = StCodes.Suspendido.value
            prefix_to_inactivate.inactivation_date = modification_date
            prefix_to_inactivate.observation = "INACTIVACIÓN MANUAL: " + observation
        
            prefix_to_inactivate.save()
        else:
            model.state_id = StCodes.Suspendido.value
            model.inactivation_date = modification_date
            model.observation = "INACTIVACIÓN MANUAL: " + observation
        
            model.save()
        return ""
    except model.DoesNotExist:
        return "El prefijo no existe"

'''
Asigna y Guarda el prefijo
'''
@transaction.atomic
def prefix_assignment(ac: CodeAssignmentRequest, enterprise, schema, persist_partial_changes, username, combination, existing_prefix, process):
    try:
        if (not existing_prefix):
            quantity = ac.Quantity
        else:
            if (process==1):
                quantity = ac.Quantity - enterprise.code_residue
            else:
                quantity = ac.Quantity

        code_type = ac.Type
        prefix_range: Range = None
        create_new_prefix = False

        quantity_range = 0
        if (ac.PrefixType == PrefixRangeType.PesoFijo.value or ac.PreferIndicatedPrefix):
            prefix_range = Range.objects.filter(id=ac.PrefixType)
        else:
            if (ac.Quantity <= enterprise.code_residue):
                prefix_range = Range.objects.filter(quantity_code= quantity).exclude(country_code= 29).first()
            else:
                if (quantity % 10 == 0):
                    quantity_range = quantity
                    prefix_range = Range.objects.filter(quantity_code= quantity_range).exclude(country_code= 29).first()
                    
                    if (not prefix_range):
                        quantity_range = int(str(1).ljust(len(str(quantity)) + 1, '0'))
                else:
                    quantity_range = int(str(1).ljust(len(str(quantity)) + 1, '0'))
                prefix_range = Range.objects.filter(quantity_code= quantity_range).exclude(country_code= 29).first()

            if (not prefix_range and not existing_prefix):                    
                return "No es posible asignar " + str(quantity) + " códigos a un prefijo."

        prefix_enterprise: Enterprise = Enterprise.objects.filter(id=enterprise.id).filter(code_residue__gte=quantity).first()

        if (not prefix_enterprise):
            assigned_prefix = Common.PrefixGenerator(prefix_range.id)
            create_new_prefix = True
        else:
            if (not existing_prefix):
                possible_prefix = Common.GetAvailablePrefix(quantity)
            else:
                possible_prefix = existing_prefix.id

            if (not possible_prefix):
                assigned_prefix = Common.PrefixGenerator(prefix_range.id)
                create_new_prefix = True
            else:
                if (ac.Quantity > enterprise.code_residue and enterprise.code_residue > 0):
                    assigned_prefix = Common.PrefixGenerator(prefix_range.id)
                    create_new_prefix = True
                else:
                    assigned_prefix = possible_prefix
        
        if (not assigned_prefix):
            return UserMessages.Msg04
        else:
            new_prefix = Prefix()

            if (create_new_prefix==True):
                new_prefix.id_prefix = assigned_prefix
                new_prefix.enterprise_id = enterprise.id
                new_prefix.state_id = StCodes.Asignado.value
                new_prefix.assignment_date = datetime.now()
                new_prefix.schema_id = schema.id
                new_prefix.range_id = prefix_range.id
                new_prefix.observation = "ASIGNACIÓN AUTOMÁTICA"
                new_prefix.validity_date = update_validity_date_prefix(new_prefix)
            else:
                new_prefix = Prefix.objects.get(id=assigned_prefix)

            if (create_new_prefix==True):
                with transaction.atomic():
                    new_prefix.save()
            
            with transaction.atomic():
                result = code_assignment(new_prefix, ac, username, prefix_range, enterprise, existing_prefix)

            
            if (create_new_prefix==True):
                if (result != ""):
                    with transaction.atomic():
                        new_prefix.delete()
                    return IntegrityError

            if (combination.give_prefix == False):
                bought_codes = min([quantity,quantity_range])

            enterprise = update_totals_enterprise(ac,enterprise)
            
            with transaction.atomic():
                enterprise.save()
            
            return "ok. Proceso completado correctamente. Se creó el prefijo: " + str(new_prefix.id_prefix)
    
    except IntegrityError as e:
        return "No fue posible guardar el prefijo." 

'''
Realiza validaciones y consultas previas a la asignación
'''
def prefix_assignation(ac: CodeAssignmentRequest, id_agreement: int= None, agreement_name: str= None, username: str= None):
    
    existing_prefix = Prefix()

    if (ac.Quantity <= 0):
        return UserMessages.Msg02

    if (ac.Schema == None):
        return UserMessages.Msg03

    try:
        enterprise: Enterprise = Enterprise.objects.filter(identification=ac.Nit).first()
        
        if (not enterprise):
            with transaction.atomic():
                enterprise = new_enterprise(ac)
                if (enterprise==False):
                    return "No fue posible crear la empresa."

        combinacion: CodeTypeBySchemas = CodeTypeBySchemas.objects.filter(code_type=ac.Type,schema_id=ac.Schema).first()
        schema: Schema = Schema.objects.filter(id=ac.Schema).first()
        process = 0

        if (not combinacion):
            return "El esquema " + str(ac.Schema) + " y el tipo de código" + str(ac.Type) + "no se pueden combinar"

        if (ac.PrefixType == PrefixRangeType.R_4D.value and ac.VariedFixedUse == True and
            ac.Type == CodeType.DerechoIdentificacionExcenNuevos.value):
            ac.PrefixType = PrefixRangeType.PesoFijo.value
        
        if (combinacion.give_prefix == 1):
            range_obj: Range = None

            if (ac.PreferIndicatedPrefix):
                range_obj = Range.objects.filter(id=int(ac.PrefixType))
            else:
                range_obj = Range.objects.all()

            if (len(range_obj) == 1):
                ac.Quantity *= range_obj.quantity_code
            else:
                ac.Quantity *= Range.objects.values_list('quantity_code', flat=True).filter(id=ac.PrefixType)[:1]
        else:
            if (ac.Quantity > enterprise.code_residue and enterprise.code_residue > 0):
                id_prefix = Common.GetAvailablePrefix(enterprise.code_residue)
                existing_prefix = Prefix.objects.get(id=id_prefix)
                process = 1
            else:
                if (ac.Quantity <= enterprise.code_residue):
                    id_prefix = Common.GetAvailablePrefix(ac.Quantity)
                    existing_prefix = Prefix.objects.get(id=id_prefix)
                else:
                    existing_prefix = None
            
        result = prefix_assignment(ac, enterprise, schema, False, username, combinacion, existing_prefix, process)
       
        if (result[:3] != "ok."):
            return "Se presentó un error. " + result
        else:
            return result

    except Exception as ex:
        return ex

@transaction.atomic
def regroup(enterprise,migration_date,user_name,prefix_request,validity_date):
    try:
        new_prefix_length: int = 11
        new_range: int = 6 # 8D
        purchased = 0
        reserved = 0
        residue = 0

        msg_request = "Prefijo: " + str(prefix_request.id_prefix) + " - Rango: " + str(prefix_request.range_id) + ". "
        prefix: Prefix = Prefix.objects.get(id_prefix=prefix_request.id_prefix,range_id=prefix_request.range_id,enterprise_id=enterprise.id)
        if (not prefix):
            return msg_request + str(UserMessages.Tmp5) + " O esta asignado a otra empresa"
        
        o_range: Range = Range.objects.filter(id=prefix_request.range_id).filter(regrouping=True)
        if (not o_range):
            return msg_request + "El rango no permite reagrupación."

        prefix.state_id = StCodes.Reagrupado.value
        
        with transaction.atomic():
            prefix.save()

        bulk_prefix=[]
        created_prefixes=[]
        q1 = Queries.PrefixToCreateFromRegroup(prefix.id,prefix_request.range_id)
        cursor= connection.cursor()
        cursor.execute(q1)
        dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id','assignment_date','assigned'])

        row_count = dpcd.shape[0]
        if (row_count <= 0):
            return "No hay prefijos a reagrupar. Por favor verifique."

        for index, row in dpcd.iterrows():
            id_pr = row['id']
            assignment_date = row['assignment_date']
            assigned = row['assigned']

            existing_prefix = Prefix.objects.filter(id_prefix=id_pr).filter(range_id=new_range).filter(state_id=2)
            if (not existing_prefix):
                new_prefix = Prefix()
                new_prefix.id_prefix = id_pr
                new_prefix.range_id = new_range
                new_prefix.enterprise_id = enterprise.id
                new_prefix.assignment_date = assignment_date
                new_prefix.regrouped = 1
                new_prefix.regrouped_parent_prefix = id_pr

                if (assigned == 1):
                    new_prefix.state_id = StCodes.Asignado.value
                    new_prefix.schema_id = 2
                    new_prefix.validity_date = validity_date
                    new_prefix.inactivation_date = None
                    new_prefix.observation = "PREFIJO REAGRUPADO"
                else:
                    new_prefix.state_id = StCodes.Suspendido_por_reagrupación_sin_derecho_al_uso.value
                    new_prefix.schema_id = 1
                    new_prefix.validity_date = datetime.now()
                    new_prefix.inactivation_date = datetime.now()
                    new_prefix.observation = "PREFIJO REAGRUPADO, SUSPENDIDO POR NO TENER CÓDIGOS ASIGNADOS/RES EN EL RANGO"
                
                bulk_prefix.append(new_prefix)
                created_prefixes.append(id_pr)
            else:
                return msg_request + " Un prefijo con este rango ya se encuentra creado en la base de datos."

        with transaction.atomic():
            Prefix.objects.bulk_create(bulk_prefix)

        with transaction.atomic():
            command = Queries.CodeRegroupDelete(created_prefixes,new_range)
            cursor= connection.cursor()
            cursor.execute(command)

        enterprise.code_quantity_reserved -= cursor.rowcount
        enterprise.code_residue += cursor.rowcount 

        with transaction.atomic():
            command = Queries.CodeRegroupUpdate(created_prefixes,new_range)
            cursor= connection.cursor()
            cursor.execute(command)
        
        enterprise.save
        return ""
    except Exception as e:
        return e
        
@transaction.atomic
def total_transfer(enterpriseO: Enterprise, enterpriseD: Enterprise, observation, user):
    obj_prefix: Prefix = Prefix.objects.filter(enterprise_id= enterpriseO.id,state_id=StCodes.Asignado.value).update(enterprise_id=enterpriseD.id,observation="FUSIÓN: " + observation)

    enterpriseD.code_quantity_purchased += enterpriseO.code_quantity_purchased
    enterpriseD.code_quantity_reserved += enterpriseO.code_quantity_reserved
    enterpriseD.code_quantity_consumed += enterpriseO.code_quantity_consumed
    enterpriseD.code_residue += enterpriseO.code_residue
    enterpriseO.code_quantity_purchased = 0
    enterpriseO.code_quantity_reserved = 0
    enterpriseO.code_quantity_consumed = 0
    enterpriseO.code_residue = 0    

    with transaction.atomic():
        enterpriseD.save()
        enterpriseO.save()
    return ""    

@transaction.atomic
def partial_transfer(prefix: PrefixId, enterpriseO: Enterprise, enterpriseD: Enterprise, observation, user):
    obj_prefix: Prefix = Prefix.objects.get(id_prefix=prefix.id_prefix,range_id=prefix.range_id)
    
    obj_prefix.enterprise_id=enterpriseD.id
    obj_prefix.observation="CESIÓN " + observation
    obj_prefix.save()
    
    obj_range: Range = Range.objects.get(id=obj_prefix.range_id)
    reserved_count = Code.objects.filter(prefix_id=obj_prefix.id).count()
    consumed_count = Code.objects.filter(prefix_id=obj_prefix.id).filter(state_id=StCodes.Asignado.value).count()

    enterpriseD.code_quantity_purchased += obj_range.quantity_code
    enterpriseD.code_quantity_reserved += reserved_count
    enterpriseD.code_quantity_consumed += consumed_count
    enterpriseD.code_residue = enterpriseD.code_quantity_purchased - enterpriseD.code_quantity_reserved
    enterpriseO.code_quantity_purchased -= obj_range.quantity_code
    enterpriseO.code_quantity_reserved -= reserved_count
    enterpriseO.code_quantity_consumed -= consumed_count
    enterpriseO.code_residue = enterpriseO.code_quantity_purchased - enterpriseO.code_quantity_reserved
    
    with transaction.atomic():
        enterpriseD.save()
        enterpriseO.save()
    return ""

def transfer(request: CodeTransfer, prefix: PrefixId):
    user = ""
    if (request.origin_nit == request.destination_nit):
        return "Los nit no pueden ser iguales"

    if (request.process == None):
        return "No se escogio un proceso válido"

    enterpriseO: Enterprise = Enterprise.objects.get(identification=request.origin_nit)
    enterpriseD: Enterprise = Enterprise.objects.get(identification=request.destination_nit)

    if (not enterpriseO):
        return UserMessages.Msg01 + str(request.origin_nit)
    
    if (not enterpriseD):
        return UserMessages.Msg01 + str(request.destination_nit)

    if (int(request.process) == TransferProcess.Total.value):
        return total_transfer(enterpriseO, enterpriseD, request.observation, user)
    else:
        return partial_transfer(prefix, enterpriseO, enterpriseD, request.observation, user)

def getPrefixesByEnterpriseId(id):
    q1 = Queries.getPrefixesByEnterprise(id)
    cursor= connection.cursor()
    cursor.execute(q1)
    dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id_prefix','type','schema','state','observation','assignment_date','validity_date','assigned','available'])

    return dpcd.iterrows