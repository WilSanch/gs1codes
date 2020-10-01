from administration.bussiness import prefix_api, prefix  
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.shortcuts import render_to_response, render
from administration.models import *
from administration.bussiness.models import CodeType as CodeT, CodeAssignmentRequest, CodeTransfer, PrefixId
from django.http import JsonResponse, HttpResponse,HttpResponseNotFound
from django.template.response import TemplateResponse
import simplejson 
import datetime
from datetime import date,timedelta
from django.shortcuts import get_object_or_404, redirect
from administration.common.functions import Common
from administration.common.constants import SchemaCodes
from django.db import transaction

# Aquí se asigna el prefijo
@login_required 
@api_view(['GET','POST'])     
def assignation(request):
    if request.method == 'GET':
        context= {}
        context['schemas'] = None
        context['enterprise'] = None
        context['prefix'] = None
        context['Error'] = None

        return render(request, 'administration/prefixTemplates/assignate.html',{"contexto": context})
    else:
        agreement_name = None
        id_agreement = None
        user_name = None

        ac = CodeAssignmentRequest
        ac.Quantity = int(request.data['quantity'])
        ac.Nit = request.data['nit']
        ac.PreferIndicatedPrefix = False
        ac.BusinessName = request.data['name']
        ac.Schema = int(request.data['schema'])
        ac.ScalePrefixes = False
        ac.Type = int(request.data['codetype'])
        ac.PrefixType = int(request.data['prefixtype'])
        ac.VariedFixedUse = False

        if (ac.PrefixType==0):
            ac.PrefixType = None
        
        resp = prefix.prefix_assignation(ac,id_agreement,agreement_name,user_name)

        option = str(request.data['nit'])
        context= {}
        enterprise:Enterprise = Enterprise.objects.get(identification=str(option))
        
        context['schemas'] = Schema.objects.all().values("id","description").order_by("id") 
        context['range'] =  None
        context['enterprise'] = enterprise
        context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
        
        if (resp != ""):
            if (resp[2:] == "ok"):
                context['Error'] = resp[3:]
            else:
                context['Error'] = resp
            return render(request, 'administration/prefixTemplates/assignate.html',{"contexto": context})

        return render(request, 'administration/prefixTemplates/assignate.html',{"contexto": context})

def load_enterprise(request):
    if request.is_ajax and request.method == "GET":
        nit = request.GET.get("nit", None)
       
        enterprise:Enterprise = Enterprise.objects.get(identification=nit)

        if (not enterprise):
            return JsonResponse({}, status = 400)
        
        return JsonResponse({"enterprise_name":enterprise.enterprise_name}, status = 200)

# -----------------------------------------------------------------------------------------------------------
# ------------------------ Busca la empresa para ejecutar la opción correspondiente ------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
@api_view(['GET','POST'])   
def assignate_search_enterprise(request): 
    if request.method == 'GET':
        context= {}
        context['enterprise_name'] = ""
        context['process'] = int(request.GET['obj'])
        return render(request, 'administration/prefixTemplates/assignate_search_enterprise.html',{"contexto": context})
    else:
        opc = int(request.POST.get('process', None))
        option = str(request.data['nit'])
        if (opc == 1):
            context= {}
            enterprise:Enterprise = Enterprise.objects.get(identification=str(option))

            if (enterprise.return_codes == False):
                enterprise.code_quantity_purchased = None
                enterprise.code_quantity_consumed = None
                enterprise.code_quantity_reserved = None
                enterprise.code_residue = None

            context['schemas'] = Schema.objects.all().values("id","description").order_by("id")
            context['range'] =  None
            context['codetype'] = None
            context['enterprise'] = enterprise
            context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
            context['Error'] = ""
            if (opc == 1):
                return render(request, 'administration/prefixTemplates/assignate.html',{"contexto": context})
            
        if (opc == 9):                        
            return redirect(reverse('enterprise_modify', args=[ option ]))

        if (opc == 10):
            prueba = request.data['nit']
            return redirect(reverse('update_ad', args=[prueba]))

        else:            
            return redirect(reverse('action_prefix', args=[ request.data['nit'],opc ]))

# -----------------------------------------------------------------------------------------------------------
# ---------------------------------- Carga los combo selects de las vistas ----------------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def load_code_types(request): # Carga los tipos de código
    schema = int(request.GET.get('schema'))
    code_types = CodeTypeBySchemas.objects.filter(schema_id=schema).order_by('-code_type_id').distinct('code_type_id')

    codetype = []
    for ct in code_types:
        code_type = CodeType.objects.get(id=ct.code_type_id)
        if (code_type.state!=0):
            data = {'id' : code_type.id, 'description': code_type.description}
            codetype.append(data)
    json_obj = simplejson.dumps(codetype)
    return HttpResponse(json_obj, content_type='application/json')

@login_required 
def load_prefix_types(request): # Carga los tipos de prefijo
    codeTypeId = int(request.GET.get('codetype'))
    schemaId = int(request.GET.get('schemaId'))

    prefixtype = []

    code_types_by_schema = CodeTypeBySchemas.objects.get(code_type_id=codeTypeId,schema_id=schemaId)
    data = {'give_prefix' : code_types_by_schema.give_prefix }
    prefixtype.append(data)

    if (schemaId == 1 and codeTypeId == 2):
        code_types_by_range = CodeTypeByRanges.objects.filter(code_type_id=codeTypeId).order_by('-range_id').distinct('range_id')
    
        for ct in code_types_by_range:
            o_range = Range.objects.get(id=ct.range_id)
            data = {'id' : o_range.id, 'description': str(o_range.name) + ' - ' + str(o_range.quantity_code) + ' codigos' }
            prefixtype.append(data)
    json_obj = simplejson.dumps(prefixtype)

    return HttpResponse(json_obj, content_type='application/json')

# -----------------------------------------------------------------------------------------------------------
# ---------------------------- Carga la tabla de prefijos dependiendo la opción -----------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def load_prefix_table(request,opc):
    opc = int(opc)
    nit = str(request.GET.get('nit'))

    context= {}
    enterprise:Enterprise = Enterprise.objects.get(identification=nit)
    
    context['opc'] = opc
    if opc == 10:
        context['prefix'] = prefix.getPrefixesByEnterpriseIdActive(enterprise.id)
    else:
        context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)

    return render(request, 'administration/Partials/prefix_table.html',{"contexto": context})

# -----------------------------------------------------------------------------------------------------------
# ---------------------------- Carga la tabla de códigos dependiendo el prefijo -----------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def load_codes_table(request):
    prefixId = int(request.GET.get('prefixId'))
    opc = int(request.GET.get('opc'))

    context= {}

    context['opc'] = opc
    context['codes'] = Code.objects.all().filter(prefix_id=prefixId).order_by('id')

    return render(request, 'administration/Partials/codes_table.html',{"contexto": context})

# -----------------------------------------------------------------------------------------------------------
# --------------------------- Ejecuta la acción del botón en la tabla de códigos ----------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def function_2nd_grid(request):
    opc = int(request.GET.get('opc'))
    codeId = int(request.GET.get('codeid'))
    if (opc == 2):
        code_obj: Code = Code.objects.get(id= codeId)
        resp = prefix.codes_inactivation(code_obj, datetime.date.today())

        if (resp == ""):
            context= {}
            context['codes'] = Code.objects.all().filter(prefix_id=code_obj.prefix_id).order_by('id')
            context['opc'] = opc
            return render(request, 'administration/Partials/codes_table.html',{"contexto": context})
        else:
            return "Error. " + resp

# -----------------------------------------------------------------------------------------------------------
# -------------------------- Ejecuta la acción del botón en la tabla de prefijos ----------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def action_prefix(request,enterprise_nit,opc):
    opc = int(opc)
    if request.method == 'GET':
        if (enterprise_nit==None):
                return HttpResponseNotFound('<h1>Page not found</h1>')

        context= {}
        enterprise:Enterprise = Enterprise.objects.get(identification=enterprise_nit)

        context['enterprise'] = enterprise
        context['Error'] = ""

        if (opc == 2):
            return render(request, 'administration/prefixTemplates/inactivate_prefix.html',{"contexto": context})
        if (opc == 3):
            return render(request, 'administration/prefixTemplates/regroup_prefix.html',{"contexto": context})
        if (opc == 4):
            return render(request, 'administration/prefixTemplates/refund_prefix.html',{"contexto": context})
    else:
        context= {}
        prefix_id = int(request.POST.get('prefixId'))
        enterprise_nit = str(request.POST.get('nit'))
        prefix_obj = get_object_or_404(Prefix, id=prefix_id)
        enterprise = get_object_or_404(Enterprise, id=prefix_obj.enterprise_id)

        if (opc==2):
            resp = prefix.prefix_inactivation(prefix_obj,datetime.date.today(),"","")

            context['opc'] = opc
            context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
        elif (opc==3):
            m_date = request.POST.get('migration_date')

            if (m_date == ""):
                return HttpResponseNotFound('<h1>Migration Date required.</h1>')

            migration_date = datetime.datetime.strptime(m_date, '%d/%m/%Y')
            schema_obj = get_object_or_404(Schema, id=prefix_obj.schema_id)
            validity_date = Common.addYears(migration_date, schema_obj.validity_time)  
            
            resp = prefix.regroup(enterprise,migration_date,"user_name",prefix_obj,validity_date)
            context['Error'] = resp

            context['opc'] = opc
            context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
        elif (opc==4):
            observation = str(request.POST.get('observation'))
            range_obj = get_object_or_404(Range, id=prefix_obj.range_id)

            with transaction.atomic():
                codes_count = Code.objects.filter(prefix_id= prefix_obj.id).count()
                codes = Code.objects.filter(prefix_id= prefix_obj.id).filter(state_id=1).delete()

                enterprise.code_quantity_reserved += range_obj.quantity_code - codes_count
                enterprise.code_residue = enterprise.code_quantity_purchased - enterprise.code_quantity_reserved
                prefix_obj.enterprise_id = None
                prefix_obj.save()
                enterprise.save()
            
            context['opc'] = opc
            context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
        elif (opc==5):
            destiny_nit = str(request.POST.get('destiny_nit'))
            observation = str(request.POST.get('observation'))
            process = int(request.POST.get('process'))

            transfer_request = CodeTransfer
            transfer_prefix = PrefixId

            transfer_request.OriginNit = enterprise_nit
            transfer_request.DestinationNit = destiny_nit
            transfer_request.Process = process
            transfer_request.Observation = observation

            transfer_prefix.id_prefix = prefix_obj.id_prefix
            transfer_prefix.range_id = prefix_obj.range_id

            with transaction.atomic():              
                resp = prefix.transfer(transfer_request,transfer_prefix)
                context['Error'] = resp

            context['opc'] = opc
            context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)                
                
        return render(request, 'administration/Partials/prefix_table.html',{"contexto": context})

# -----------------------------------------------------------------------------------------------------------
# ------------------------------------------ Cesión de códigos ----------------------------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def transfer_prefix(request):
    if request.method == 'GET':        
        context= {}

        context['Error'] = ""
        return render(request, 'administration/prefixTemplates/transfer_prefix.html',{"contexto": context})    
    
# -----------------------------------------------------------------------------------------------------------
# ----------------------------- Actualización masiva de la fecha de vigencia --------------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def update_validity_date_prefix(request):
    schema = get_object_or_404(Schema, id=SchemaCodes.RenovacionAnual31Diciembre.value)
    prefix_count = Prefix.objects.filter(schema_id= schema.id).count()
    if request.method == 'GET':        
        context= {}

        context['Error'] = ""
        context['schema_date'] = schema.validity_date.strftime('%d/%m/%Y')
        context['prefix_count'] = prefix_count
        return render(request, 'administration/prefixTemplates/update_validity_date.html',{"contexto": context})    
    else:
        new_date = request.POST.get("new_date", None)
        schema_obj = Schema.objects.get(id=SchemaCodes.RenovacionAnual31Diciembre.value)

        validity_date = datetime.datetime.strptime(new_date, '%d/%m/%Y')

        with transaction.atomic():
            schema_obj.validity_date = validity_date
            schema_obj.save()
            date_prefix = validity_date + timedelta(days=1)
            Prefix.objects.filter(schema_id=SchemaCodes.RenovacionAnual31Diciembre.value).update(validity_date=date_prefix)

        context= {}

        context['Error'] = "Se actualizó la fecha correctamente"
        context['schema_date'] = new_date
        context['prefix_count'] = prefix_count
        
        return render(request, 'administration/prefixTemplates/update_validity_date.html',{"contexto": context})    

# -----------------------------------------------------------------------------------------------------------
# ----------------------------- Creación o modificación de empresa --------------------------------
# -----------------------------------------------------------------------------------------------------------
@login_required 
def enterprise_modify(request, enterprise):
    if request.method == 'GET':        
        context= {}
        enterprise_obj: Enterprise = Enterprise.objects.filter(identification=enterprise).first()
        if (not enterprise_obj):
            enterprise_obj = Enterprise()
            enterprise_obj.identification = enterprise
            enterprise_obj.code_quantity_consumed = 0
            enterprise_obj.code_quantity_purchased = 0
            enterprise_obj.code_quantity_reserved = 0
            enterprise_obj.code_residue = 0

        context['enterprise'] = enterprise_obj
        context['Error'] = ""
        return render(request, 'administration/enterpriseTemplates/enterprise.html',{"contexto": context})    
    else:        
        nit = request.POST.get("nit", None)
        name = request.POST.get("name", None)
        purchased = request.POST.get("purchased", None)
        consumed = request.POST.get("consumed", None)
        reserved = request.POST.get("reserved", None)
       # observation = request.POST.get("observation", None)

        enterprise_to_modify: Enterprise = Enterprise.objects.filter(identification=nit).first()

        if not(enterprise_to_modify):
            enterprise_to_modify = Enterprise()
            enterprise_to_modify.identification = nit
        
        enterprise_to_modify.enterprise_name = name
        enterprise_to_modify.code_quantity_purchased = int(purchased)
        enterprise_to_modify.code_quantity_reserved = int(reserved)
        enterprise_to_modify.code_quantity_consumed = int(consumed)
        enterprise_to_modify.code_residue = 0
        enterprise_to_modify.country_id = 170
        enterprise_to_modify.enterprise_state = True
        
        with transaction.atomic():
            enterprise_to_modify.save()
        
        context= {}
        context['Error'] = "Se guardó la empresa correctamente"
        context['enterprise'] = enterprise_to_modify
        
        return render(request, 'administration/enterpriseTemplates/enterprise.html',{"contexto": context})    

@login_required 
@api_view(['GET', 'POST'])
def updateAd(request,enterprise_nit):
    if "GET" == request.method:
        context= {}
        enterprise_obj = Enterprise.objects.filter(identification=enterprise_nit).first()
        if (not enterprise_obj):
            context['Error'] = "No se encontró la empresa"

        context['Error'] = ""
        context['enterprise'] = enterprise_obj
        return render(request, 'administration/prefixTemplates/update_ad.html',{"contexto": context})
    if "POST" == request.method:
        c = Code()
        c.id = request.POST['id']
        c.description = request.POST['description']
        c.save(update_fields=['description'])
        
        context= {}
        context['Error'] = "Se guardó la empresa correctamente"
        return render(request, 'administration/prefixTemplates/update_ad.html',{"contexto": context})