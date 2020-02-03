from administration.bussiness.models import CodeAssignmentRequest
from administration.models import Enterprise
from django.db import models

def new_enterprise(ac: CodeAssignmentRequest):
    try:
        enterprise: Enterprise = None
        
        enterprise.identification = ac.Nit
        enterprise.enterprise_name = ac.BusinessName
        enterprise.code_quantity_purchased = 0
        enterprise.code_quantity_consumed = 0
        enterprise.code_residue = 0
        enterprise.enterprise_state = True

        enterprise.save()

        return enterprise
    except IntegrityError:
        return False

def update_totals_enterprise(ac: CodeAssignmentRequest, enterprise: Enterprise):
    enterprise.code_quantity_purchased = 0 if enterprise.code_quantity_purchased == None else enterprise.code_quantity_purchased
    enterprise.code_residue = 0 if enterprise.code_residue == None else enterprise.code_residue
    enterprise.code_quantity_reserved = 0 if enterprise.code_quantity_reserved == None else enterprise.code_quantity_reserved
    enterprise.code_quantity_consumed = 0 if enterprise.code_quantity_consumed == None else enterprise.code_quantity_consumed

    if (ac.Quantity >= enterprise.code_residue):
        ac.Quantity -= int(enterprise.code_residue)
        enterprise.code_quantity_purchased += enterprise.code_residue
        enterprise.code_quantity_reserved += enterprise.code_residue
        enterprise.code_residue = 0
    else:
        enterprise.code_quantity_purchased += ac.Quantity
        enterprise.code_quantity_reserved += ac.Quantity
        enterprise.code_residue -= ac.Quantity
        ac.Quantity = 0

    return enterprise