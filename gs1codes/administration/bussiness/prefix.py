from typing import TypedDict, List
import datetime
from datetime import datetime, date
import json
from administration.models.core import Prefix,Schema,Enterprise,CodeTypeByRanges,CodeTypeBySchemas, Range, Code, CodeType as ModelCodeType
from administration.bussiness.models import PrefixId, ActivationInactivationBM, MarkCodeRespose, CodeAssignmentRequest, CodeAssignation
from datetime import datetime
from django.db import connection,transaction, IntegrityError
from administration.bussiness.models import *
from administration.bussiness.enterprise import new_enterprise, update_totals_enterprise
from administration.bussiness.codes import code_assignment
from administration.common.constants import UserMessages, PrefixRangeType, CodeType as Code_Type, StCodes
from administration.common.functions import Common,Queries
import pandas as pd
from administration.bussiness.activate import *

def update_validity_date_prefix(model: Prefix):
    schema:Schema = Schema.objects.filter(id=model.schema_id).first()
    if (not schema):
        return False
    else:
        if (schema.validity_date == None):
            if (schema.validate_from_creation_date == False):
                model.validity_date = Common.addYears(model.assignment_date, schema.validity_time)
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


def codes_inactivation(code_to_inactivate, modification_date):
    if (not code_to_inactivate):
        return "El prefijo no existe"

    if (code_to_inactivate.state_id == StCodes.Suspendido.value):
        return codes_activation(code_to_inactivate,modification_date)

    if (code_to_inactivate.state_id != StCodes.Asignado.value):
        return "Solo es posible inactivar un código asignado. Por favor verifique!"
    
    code_to_inactivate.state_id = StCodes.Suspendido.value

    code_to_inactivate.save()

    return ""

def codes_activation(code_to_activate, modification_date):
    if (not code_to_activate):
        return "El prefijo no existe"

    if (code_to_activate.state_id == StCodes.Asignado.value):
        return codes_inactivation(code_to_activate,modification_date)

    if (code_to_activate.state_id != StCodes.Suspendido.value):
        return "Solo es posible activar un código suspendido. Por favor verifique!"
    
    code_to_activate.state_id = StCodes.Asignado.value

    code_to_activate.save()

    return ""

def prefix_inactivation(model: Prefix, modification_date, observation, user):
    try:
        if (model.state_id == StCodes.Suspendido.value):
            return prefix_activation(model, modification_date, observation, user)

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

# -----------------------------------------------------------------------------------------------------------------
# Asigna y Guarda el prefijo
# -----------------------------------------------------------------------------------------------------------------

@transaction.atomic
def prefix_assignment(ac: CodeAssignmentRequest, enterprise, schema, persist_partial_changes, username, combination, existing_prefix, selected_range):
    try:
        create_new_prefix = False

        if (combination.give_prefix == 0):
            if (not existing_prefix):
                quantity = ac.Quantity
                create_new_prefix = True
            else:
                quantity = ac.Quantity - existing_prefix.code_residue
                if (quantity <= 0):
                    create_new_prefix = False
                else:
                    create_new_prefix = True
        else:
            quantity = int(ac.Quantity / selected_range.quantity_code)
            create_new_prefix = True
        
        new_prefix = Prefix()

        if (combination.give_prefix == 1):
            ac.Quantity = selected_range.quantity_code

           
            list_registry = []
                
            for x in range(1, quantity+1):
                with transaction.atomic():
                    assigned_prefix = Common.PrefixGenerator(selected_range.id)

                    new_prefix.id_prefix = assigned_prefix
                    new_prefix.enterprise_id = enterprise.id
                    new_prefix.state_id = StCodes.Asignado.value
                    new_prefix.assignment_date = datetime.now()
                    new_prefix.schema_id = schema.id
                    new_prefix.range_id = selected_range.id
                    new_prefix.observation = "ASIGNACIÓN AUTOMÁTICA"
                    new_prefix.validity_date = update_validity_date_prefix(new_prefix)
                    new_prefix.code_quantity_consumed = 0
                    new_prefix.code_quantity_purchased = selected_range.quantity_code
                    new_prefix.code_quantity_reserved = selected_range.quantity_code
                    new_prefix.code_residue = 0
                    
                    new_prefix.save()

                    pref_registry = PrefixRegistry()
                    pref_registry["key"] = str(new_prefix.id_prefix)
                    pref_registry["type"] = "gcp"
                    pref_registry["companyName"] = enterprise.enterprise_name
                    pref_registry["status"] = 1

                    list_registry.append(pref_registry)

                    pref_registry = PrefixRegistry()

                    with transaction.atomic():
                        result = code_assignment(new_prefix, ac, username, selected_range, enterprise, existing_prefix)

                    new_prefix = Prefix() 
            
            lista_prefix = ListPref()
            lista_prefix['listpref'] = list_registry

            # Add license batch
            rta = AddLicenseBatch(lista_prefix)
        else:
            if (create_new_prefix == True):
                assigned_prefix = Common.PrefixGenerator(selected_range.id)

                new_prefix.id_prefix = assigned_prefix
                new_prefix.enterprise_id = enterprise.id
                new_prefix.state_id = StCodes.Asignado.value
                new_prefix.assignment_date = datetime.now()
                new_prefix.schema_id = schema.id
                new_prefix.range_id = selected_range.id
                new_prefix.observation = "ASIGNACIÓN AUTOMÁTICA"
                new_prefix.validity_date = update_validity_date_prefix(new_prefix)
                new_prefix.code_quantity_purchased = selected_range.quantity_code
                new_prefix.code_quantity_reserved = quantity
                new_prefix.code_residue = selected_range.quantity_code - quantity
            
                with transaction.atomic():
                    new_prefix.save()

                pref_registry = PrefixRegistry()
                
                pref_registry["key"] = str(new_prefix.id_prefix)
                pref_registry["type"] = "gcp"
                pref_registry["companyName"] = enterprise.enterprise_name
                pref_registry["status"] = 1

                with transaction.atomic():
                    result = code_assignment(new_prefix, ac, username, selected_range, enterprise, existing_prefix)

                # Add license 
                rta = AddLicense(pref_registry)
                result = rta

            if (existing_prefix is not None):
                if (create_new_prefix == True):
                    existing_prefix.code_quantity_reserved += existing_prefix.code_residue
                    existing_prefix.code_residue -=  existing_prefix.code_residue
                else:
                    existing_prefix.code_quantity_reserved += ac.Quantity
                    existing_prefix.code_residue -= ac.Quantity

                with transaction.atomic():
                    existing_prefix.save()                    
                    result = ""
       
        if (result != ""):
            transaction.set_rollback(True)
            return result
        
        enterprise = update_totals_enterprise(ac,enterprise,selected_range)
        
        with transaction.atomic():
            enterprise.save()
        
        if (create_new_prefix == True):
            return "ok.Proceso completado correctamente. Se creó el prefijo: " + str(new_prefix.id_prefix)
        else:
            return "ok.Proceso completado correctamente. Se asignaron los códigos al prefijo: " + str(existing_prefix.id_prefix)
    except IntegrityError as e:
        return "No fue posible guardar el prefijo." 

# --------------------------------------------------------------------------------------------------------------
# Realiza validaciones y consultas previas a la asignación
# --------------------------------------------------------------------------------------------------------------
def prefix_assignation(ac: CodeAssignmentRequest, id_agreement: int= None, agreement_name: str= None, username: str= None):
    
    existing_prefix = Prefix()

    if (ac.Quantity <= 0):
        return UserMessages.Msg02

    if (ac.Schema == None):
        return UserMessages.Msg03

    try:
        ac.Type = int(ac.Type)

        if (ac.Quantity<=0):
            return "La cantidad requerida no puede ser cero o menor que cero. Por favor verifique!"


        enterprise: Enterprise = Enterprise.objects.filter(identification=ac.Nit).first()
        
        if (not enterprise):
            with transaction.atomic():
                enterprise = new_enterprise(ac)
                if (enterprise==False):
                    return "No fue posible crear la empresa."

        combinacion: CodeTypeBySchemas = CodeTypeBySchemas.objects.filter(code_type_id=ac.Type,schema_id=ac.Schema).first()
        schema: Schema = Schema.objects.filter(id=ac.Schema).first()

        if (not combinacion):
            return "El esquema " + str(ac.Schema) + " y el tipo de código" + str(ac.Type) + " no se pueden combinar"

        if (ac.PrefixType == PrefixRangeType.R_4D.value and ac.VariedFixedUse == True and
            ac.Type == Code_Type.DerechoIdentificacionExcenNuevos.value):
            ac.PrefixType = PrefixRangeType.PesoFijo.value
        
        range_obj = None
        existing_prefix = None

        code_type_obj = ModelCodeType.objects.filter(id=ac.Type).first()

        if not(ac.PrefixType):
            code_type_by_range = CodeTypeByRanges.objects.filter(code_type_id=code_type_obj.id)

            if (ac.Quantity%10==0 or ac.Quantity==1) and (str(ac.Quantity)[1:1] == '1' ):
                tmp_quantity = ac.Quantity
            else:
                tmp_quantity = int( "1".ljust(len(str(ac.Quantity))+1, '0') )

            if (not code_type_by_range):
                return "No existen rangos para el tipo de código seleccionado. Por favor verifique!"
            else:
                if (code_type_by_range.count() > 1):
                    for obj in code_type_by_range:
                        range_obj = Range.objects.filter(id=obj.range_id).filter(quantity_code=tmp_quantity).first()
                        if not(range_obj):
                            range_obj = None
                        else:
                            break
                else:
                    for obj in code_type_by_range:
                        range_obj = Range.objects.get(id=obj.range_id)
                    if (not range_obj):
                        return "no se encontró un rango para el tipo de prefijo"
        else:
            range_obj = Range.objects.filter(id=ac.PrefixType).first()

        if (not range_obj):
            return "Error. No fue posible encontrar el rango"

        if (combinacion.give_prefix == 1):
            if (ac.PreferIndicatedPrefix):
                range_obj = Range.objects.get(id=ac.PrefixType)
                ac.Quantity *= range_obj.quantity_code

                if (ac.Quantity > range_obj.quantity_code):
                    return "La cantidad de códigos seleccionada no puede ser mayor a la cantidad de códigos para ese rango"
            else:
                ac.Quantity *= range_obj.quantity_code

            existing_prefix = None
        else:
            id_prefix = Common.GetIdAvailablePrefix(enterprise.id,range_obj.id)
            if (not id_prefix):
                existing_prefix = None
            else:
                existing_prefix = Prefix.objects.get(id=id_prefix)
            
        result = prefix_assignment(ac, enterprise, schema, False, username, combinacion, existing_prefix, range_obj)
       
        if (result[:3] != "ok."):
            return "Se presentó un error. " + result
        else:
            return result[3:]

    except Exception as ex:
        return ex

@transaction.atomic
def regroup(enterprise,migration_date,user_name,prefix,validity_date):
    try:
        new_prefix_length: int = 11
        new_range: int = 6 # 8D
        purchased = 0
        reserved = 0
        residue = 0

        msg_request = "Prefijo: " + str(prefix.id_prefix) + " - Rango: " + str(prefix.range_id) + ". "
        
        if (not prefix):
            return msg_request + str(UserMessages.Tmp5) + " O esta asignado a otra empresa"
        
        o_range: Range = Range.objects.filter(id=prefix.range_id).filter(regrouping=True)
        if (not o_range):
            return msg_request + "El rango no permite reagrupación."

        prefix.state_id = StCodes.Reagrupado.value
        
        with transaction.atomic():
            prefix.save()

        bulk_prefix=[]
        created_prefixes=[]
        q1 = Queries.PrefixToCreateFromRegroup(prefix.id,prefix.range_id)
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
    if (request.OriginNit == request.DestinationNit):
        return "Los nit no pueden ser iguales"

    if (request.Process == None):
        return "No se escogio un proceso válido"

    enterpriseO: Enterprise = Enterprise.objects.get(identification=request.OriginNit)
    enterpriseD: Enterprise = Enterprise.objects.get(identification=request.DestinationNit)

    if (not enterpriseO):
        return UserMessages.Msg01 + str(request.OriginNit)
    
    if (not enterpriseD):
        return UserMessages.Msg01 + str(request.DestinationNit)

    if (int(request.Process) == TransferProcess.Total.value):
        return total_transfer(enterpriseO, enterpriseD, request.Observation, user)
    else:
        return partial_transfer(prefix, enterpriseO, enterpriseD, request.Observation, user)

def getPrefixesByEnterpriseId(id):
    q1 = Queries.getPrefixesByEnterprise(id)
    cursor= connection.cursor()
    cursor.execute(q1)
    dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id_prefix','quantity_code','type','schema','state','observation','assignment_date','validity_date','assigned','available','id','state_id','regrouping'])

    return dpcd.iterrows

def getPrefixesByEnterpriseIdActive(id):
    q1 = Queries.getPrefixesByEnterpriseActive(id)
    cursor= connection.cursor()
    cursor.execute(q1)
    dpcd =  pd.DataFrame(cursor.fetchall(), columns=['id_prefix','quantity_code','type','schema','state','observation','assignment_date','validity_date','assigned','available','id','state_id','regrouping'])
    return dpcd.iterrows

