from administration.bussiness.models import CodeAssignmentRequest
from administration.models import Enterprise, Range
from django.db import models, IntegrityError

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

def update_totals_enterprise(ac: CodeAssignmentRequest, enterprise: Enterprise, obj_range: Range):
    enterprise.code_quantity_purchased = 0 if enterprise.code_quantity_purchased == None else enterprise.code_quantity_purchased
    enterprise.code_residue = 0 if enterprise.code_residue == None else enterprise.code_residue
    enterprise.code_quantity_reserved = 0 if enterprise.code_quantity_reserved == None else enterprise.code_quantity_reserved
    enterprise.code_quantity_consumed = 0 if enterprise.code_quantity_consumed == None else enterprise.code_quantity_consumed

    if (ac.Quantity <= enterprise.code_residue):
        if (enterprise.code_residue == 0):
            enterprise.code_residue += int(str(1).ljust(len(str(ac.Quantity)) + 1, '0'))
            enterprise.code_quantity_purchased += obj_range.quantity_code
            enterprise.code_quantity_reserved += ac.Quantity
            enterprise.code_residue -= ac.Quantity

            enterprise.code_residue -= ac.Quantity
            enterprise.code_quantity_reserved += ac.Quantity
        else:
            enterprise.code_residue -= ac.Quantity
            enterprise.code_quantity_reserved += ac.Quantity
    else:
        purchased = 0
        if (len(str(ac.Quantity)) >= 1):
            purchased += obj_range.quantity_code
        else:
            purchased = ac.Quantity - enterprise.code_residue
        enterprise.code_quantity_purchased += purchased
    
        reserved = ac.Quantity
        enterprise.code_quantity_reserved += reserved

        residue = enterprise.code_quantity_purchased - enterprise.code_quantity_reserved
        enterprise.code_residue = residue
        
    
    return enterprise