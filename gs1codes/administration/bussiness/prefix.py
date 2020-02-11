from typing import TypedDict, List
import datetime
from datetime import datetime, date
import json
from django.db import transaction
from administration.models.core import Prefix,Schema,Enterprise,CodeTypeByRanges,CodeTypeBySchemas, Range  
from administration.bussiness.models import PrefixId, ActivationInactivationBM, MarkCodeRespose, CodeAssignmentRequest, CodeAssignation
from administration.bussiness.enterprise import new_enterprise, update_totals_enterprise
# from administration.bussiness.codes import code_assignment
from administration.common.constants import UserMessages, PrefixRangeType, CodeType, StCodes
from administration.common.functions import Common
from django.db.models import Q

def update_validity_date(model: Prefix):
    schema:Schema = Schema.objects.filter(id=model.schema_id).first()
    #enterprise: Enterprise = Enterprise.objects.get(id=model.enterprise)  'description',
    
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
        if (model.state_id == StCodes.NoReutilizable.value):
            return "No puede activar un prefijo cuyo estado es NO REUTILIZABLE"
        else:
            model.state_id = StCodes.Asignado.value
            model.assignment_date = assignment_date
            model.observation = "ACTIVACIÓN MANUAL: " + observation
            model.validity_date = update_validity_date(model)  
            model.save()

        return ""

    except model.DoesNotExist:
        return "El prefijo no existe"
    #ActualizarHistoricoPrefijo(pr);

def activation(prefixes: ActivationInactivationBM) -> MarkCodeRespose:
    user = "User.Identity.name"
    result = ""
    resp = ""

    for pr in prefixes['Prefixes']:
        model: Prefix = Prefix.objects.get(id_prefix=pr['Id'],range_id=pr['Range'])
        resp = prefix_activation(model, prefixes['AssignmentDate'], prefixes['Observation'], user)

        if (resp != ""):
            result = "No fue posible activar el prefijo " + str(pr['Id']) + " Rango: " + str(pr['Range']) + resp
            break

    if (result == ""):
        return {
            "MensajeUI": "Proceso completado correctamente.",
            "Respuesta": 200
        }    
    else:
        return {
            "MensajeUI": "No fue posible procesar la solicitud. Error: " + result,
            "Respuesta": 400
        }


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

def inactivation (prefixes: ActivationInactivationBM) -> MarkCodeRespose:
    user = "User.Identity.name"
    result = ""
    resp = ""

    for pr in prefixes['Prefixes']:
        model: Prefix = Prefix.objects.get(id_prefix=pr['Id'],range_id=pr['Range'])
        resp = prefix_inactivation(model, prefixes['AssignmentDate'], prefixes['Observation'], user)

        if (resp != ""):
            result = "No fue posible inactivar el prefijo " + str(pr['Id']) + " Rango: " + str(pr['Range']) + resp
            break

    if (result == ""):
        return {
            "MensajeUI": "Proceso completado correctamente.",
            "Respuesta": 200
        }    
    else:
        return {
            "MensajeUI": "No fue posible procesar la solicitud. Error: " + result,
            "Respuesta": 400
        }

'''
Asigna y Guarda el prefijo
'''
def prefix_assignment(ac: CodeAssignmentRequest, enterprise: Enterprise, schema: Schema, persist_partial_changes: bool, username: str, combination: CodeTypeBySchemas):
    quantity = ac.Quantity
    code_type = ac.Type
    prefix_range: Range = None

    try:
        quantity_range = 0
        if (ac.PrefixType == PrefixRangeType.PesoFijo.value or ac.PreferIndicatedPrefix):
            prefix_range = Range.objects.filter(id=ac.PrefixType)
        else:
            prefix_range = Range.objects.filter(quantity_code= quantity).exclude(country_code= 29).first()

            if (not prefix_range):                    
                quantity_range = int(str(1).ljust(len(str(quantity)) + 1, '0'))
                prefix_range = Range.objects.filter(quantity_code= quantity_range).exclude(country_code= 29).first()
                if (not prefix_range):
                    return "No es posible asignar " + str(quantity) + " códigos a un prefijo."

        assigned_prefix = Common.PrefixGenerator(prefix_range.id)
        if (assigned_prefix != None):
            new_prefix = Prefix()

            new_prefix.id_prefix = assigned_prefix
            new_prefix.enterprise_id = enterprise.id
            new_prefix.state_id = StCodes.Asignado.value
            new_prefix.assignment_date = datetime.now()
            new_prefix.schema_id = schema.id
            new_prefix.range_id = prefix_range.id
            new_prefix.observation = "ASIGNACIÓN AUTOMÁTICA"
            new_prefix.validity_date = update_validity_date(new_prefix)

            with transaction.atomic():
                new_prefix.save()
            
            # with transaction.atomic():
            #     result = code_assignment(new_prefix, ac, username, prefix_range)

            if (result != ""):
                raise IntegrityError

            if (combination.give_prefix == False):
                bought_codes = min([quantity,quantity_range])

                enterprise.code_quantity_purchased += bought_codes
                enterprise.code_quantity_reserved += bought_codes
                enterprise.code_residue = quantity_range - bought_codes

            quantity -= quantity_range 
            with transaction.atomic():
                enterprise.save()

            return ""
        else:
            return UserMessages.Msg04
    except IntegrityError as e:
        return "No fue posible guardar el prefijo." 



'''
Realiza validaciones y consultas previas a la asignación
'''
def prefix_assignation(ac: CodeAssignmentRequest, id_agreement: int= None, agreement_name: str= None, username: str= None):
    
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
            enterprise = update_totals_enterprise(ac,enterprise)

        result = prefix_assignment(ac, enterprise, schema, False, username, combinacion)
        if (result != ""):
            return "Se presentó un error. " + result

        return {
            "MensajeUI": "Pruebas realizadas correctamente",
            "Respuesta": 200
        }    
    except Exception as ex:
        return ex

def Test(obj: CodeAssignation) -> MarkCodeRespose:
    agreement_name = obj['AgreementName']

    id_agreement = obj['IdAgreement']
    user_name = obj['UserName']
    ac = CodeAssignmentRequest

    for pr in obj['Request']:
        ac.Quantity = pr['Quantity']
        ac.Nit = pr['Nit']
        ac.PreferIndicatedPrefix = pr['PreferIndicatedPrefix']
        ac.BusinessName = pr['BusinessName']
        ac.Schema = pr['Schema']
        ac.ScalePrefixes = pr['ScalePrefixes']
        ac.Type = pr['Type']
        ac.PrefixType = pr['PrefixType']
        ac.VariedFixedUse = pr['VariedFixedUse']
        resp = prefix_assignation(ac,id_agreement,agreement_name,user_name)

    return {
        "MensajeUI": resp,
        "Respuesta": 200
    }    
    