from datetime import datetime
from django.db import transaction
from administration.models.core import Prefix,Schema,Enterprise,Range,Code
from administration.bussiness.models import *
from administration.common.constants import UserMessages, StCodes
from administration.common.functions import Common
from administration.bussiness.prefix import prefix_activation,prefix_inactivation,prefix_assignation,regroup,transfer

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

def assignate_prefix(obj: CodeAssignation) -> MarkCodeRespose:
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


def prefix_regroup(data: RegroupBM) -> MarkCodeRespose:
    try:
        nit = data['Nit']
        enterprise: Enterprise = Enterprise.objects.filter(identification=nit).first()

        if (not enterprise):
            return {
                "MensajeUI": Msg01 + str(nit),
                "Respuesta": 200
                }

        migration_date = data['ContractMigrationDate']
        user_name = data['UserName']
        
        if (migration_date==None):
            migration_date = datetime.now()
        else:
            migration_date = datetime.strptime(migration_date,'%Y-%m-%d')

        schema: Schema = Schema.objects.get(id=2)

        validity_date = Common.addYears(migration_date, schema.validity_time)   
        
        prefix_request= PrefixId

        with transaction.atomic():
            for pr in data['Prefixes']:
                prefix_request.id_prefix = int(pr['Id'])
                prefix_request.range_id = int(pr['Range'])

                if (prefix_request.range_id == 6):
                    result = "No es posible reagrupar un 8D."
                else:
                    result = regroup(enterprise,migration_date,user_name,prefix_request,validity_date)

                if (result != ""):
                    transaction.set_rollback(True)
                    return {
                        "MensajeUI": result,
                        "Respuesta": 200
                        }

        return {
            "MensajeUI": "Proceso completado correctamente",
            "Respuesta": 200
            }    

    except Exception as e:
        return e

def prefix_transfer(data: CodeTransfer):
    try:
        request = CodeTransfer

        request.origin_nit = data['OriginNit']
        request.destination_nit = data['DestinationNit']
        request.process = data['Process']
        request.observation = data['Observation']

        prefix = PrefixId

        with transaction.atomic():
            for pr in data['Prefixes']:
                prefix.id_prefix = int(pr['Id'])
                prefix.range_id = int(pr['Range'])

                result = transfer(request,prefix)

                if (result != ""):
                    transaction.set_rollback(True)
                    return {
                        "MensajeUI": result,
                        "Respuesta": 200
                        }
                else:
                    return {
                        "MensajeUI": "Proceso completado correctamente",
                        "Respuesta": 200
                        }    

    except Exception as e:
        return e

def prefix_refund(data: PrefixRefund):
    try:
        nit = data['Nit']
        observation = data['Observation']

        enterprise: Enterprise = Enterprise.objects.get(identification=nit)

        if (not enterprise):
            return {
                "MensajeUI": UserMessages.Msg01,
                "Respuesta": 200
                }
        
        with transaction.atomic():
            for pr in data['Prefixes']:
                idprefix = int(pr['Id'])
                rangeid = int(pr['Range'])

                prefix_obj = Prefix.objects.filter(id_prefix = idprefix,range_id= rangeid,enterprise_id= enterprise.id).first()
                if (not prefix_obj):
                    return {
                        "MensajeUI": UserMessages.Msg06,
                        "Respuesta": 200
                        }

                prefix= Prefix.objects.filter(id_prefix = idprefix,range_id= rangeid,enterprise_id= enterprise.id).update(state=StCodes.Suspendido.value,observation="DEVOLUCIÓN: " + observation)
                range_obj:Range = Range.objects.get(id=prefix_obj.range_id)

                if (prefix > 0):                    
                    codes_count = Code.objects.filter(prefix_id= prefix_obj.id).count()
                    codes = Code.objects.filter(prefix_id= prefix_obj.id).filter(state_id=1).delete()

        with transaction.atomic():    
            enterprise.code_quantity_reserved += range_obj.quantity_code - codes_count
            enterprise.code_residue = enterprise.code_quantity_purchased - enterprise.code_quantity_reserved
            enterprise.save()
            
        return {
            "MensajeUI": "Proceso completado correctamente",
            "Respuesta": 200
            }    

    except Exception as e:
        return e

def masive_update_validity_date(validity_date: datetime):
    try:
        schemas = Schema.objects.exclude(validity_date=None)

        with transaction.atomic():
            for schema in schemas:
                prefixes = Prefix.objects.filter(schema_id=schema.id,state_id=StCodes.Asignado.value)

                schema.validity_date= validity_date
                prefixes.update(validity_date= validity_date)
                schema.save()
        
        return {
            "MensajeUI": "Proceso completado correctamente",
            "Respuesta": 200
            }
    except Exception as e:
        return e
