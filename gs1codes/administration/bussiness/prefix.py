from enum import Enum
from typing import TypedDict, List
from administration.models.core import Prefix,Schema,Enterprise
import datetime
from datetime import datetime, date
import json

class States(Enum):
    Disponible = 1
    Asignado = 2
    Suspendido = 3
    Reagrupado = 4
    NoReutilizable = 5
    UsoGS1 = 6
    Reservado_Migracion = 9
    PendienteProceso = 10
    Procesado = 11
    SuspendidoPorReagrupacion = 12
    Cesion = 13

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
    


def addYears(date_to_add, years):
    try:
    #Devuelve el mismo dia del año correspondiente
        return date_to_add.replace(year = date_to_add.year + years)
    except ValueError:
    #Si no es el mismo día, retornará otro, es decir, del 29 de febrero al 1 de marzo, etc.
        return date_to_add + (date(date_to_add.year + years, 1, 1) - date(date_to_add.year, 1, 1))


def update_validity_date(model: Prefix):
    schema:Schema = Schema.objects.get(id=model.schema_id)
    #enterprise: Enterprise = Enterprise.objects.get(id=model.enterprise)  'description',
    
    if (schema != None):
        if (schema.validity_date == None):
            if (schema.validate_from_creation_date == False):
                model.validity_date = addYears(model.assignment_date, schema.validity_time)
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

def activation(prefixes: ActivationInactivationBM, user) -> MarkCodeRespose:
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
            

def Pruebas(obj: ActivationInactivationBM) -> MarkCodeRespose:
    resp = activation(obj)

    return {
        "MensajeUI": resp,
        "Respuesta": 200
    }    
    