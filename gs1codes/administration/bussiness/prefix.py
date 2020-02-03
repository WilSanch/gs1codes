from typing import TypedDict, List
from administration.common.constants import States
from administration.common.functions import Common
from administration.models.core import Prefix,Schema,Enterprise

import datetime
from datetime import datetime, date
import json

class PrefixId(TypedDict):
    Id: str
    Range: int

class ActivationInactivationBM(TypedDict):
    Prefixes: PrefixId
    Observation: str
    AssignmentDate: None

class MarkCodeRespose(TypedDict):
    MensajeUI: str
    Respuesta: int
    
def update_validity_date(model: Prefix):
    schema:Schema = Schema.objects.get(id=model.schema_id)
    #enterprise: Enterprise = Enterprise.objects.get(id=model.enterprise)  'description',
    
    if (schema != None):
        if (schema.validity_date == None):
            if (schema.validate_from_creation_date == False):
                model.validity_date = Common.AddYears(model.assignment_date, schema.validity_time)
        else:
            model.validity_date = schema.validity_date

    return model.validity_date


def prefix_activation(model: Prefix, assignment_date, observation, user):
    try:
        if (model.state_id == States.NoReutilizable.value):
            return "No puede activar un prefijo cuyo estado es NO REUTILIZABLE"
        else:
            model.state_id = States.Asignado.value
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
            prefix_to_inactivate.state_id = States.Suspendido.value
            prefix_to_inactivate.inactivation_date = modification_date
            prefix_to_inactivate.observation = "INACTIVACIÓN MANUAL: " + observation
        
            prefix_to_inactivate.save()
        else:
            model.state_id = States.Suspendido.value
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

# def prefix_release()

def Pruebas(obj: ActivationInactivationBM) -> MarkCodeRespose:
    resp = activation(obj)

    return {
        "MensajeUI": resp,
        "Respuesta": 200
    }    
    