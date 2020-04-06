from administration.bussiness import prefix_api, prefix  
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from django.shortcuts import render_to_response, render
from administration.models import *
from administration.bussiness.models import *

# Aquí se asigna el prefijo
@login_required 
@api_view(['GET','POST'])     
def assignation(request):
    if request.method == 'GET':
        context= {}
        enterprise:Enterprise = Enterprise.objects.get(identification='890900608')

        context['schemas'] = Schema.objects.all().values("id","description").order_by("id")        
        context['enterprise'] = enterprise
        context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
        context['Error'] = ""

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
        ac.Type = 55600
        ac.PrefixType = None
        ac.VariedFixedUse = False
        
        resp = prefix.prefix_assignation(ac,id_agreement,agreement_name,user_name)

        context= {}
        enterprise:Enterprise = Enterprise.objects.get(identification='10203040')
        
        context['schemas'] = Schema.objects.all().values("id","description").order_by("id")        
        context['enterprise'] = enterprise
        context['prefix'] = prefix.getPrefixesByEnterpriseId(enterprise.id)
        
        if (resp != ""):
            context['Error'] = resp
            return render(request, 'administration/prefixTemplates/assignate.html',{"contexto": context})

        return render(request, 'administration/prefixTemplates/assignate.html',{"contexto": context})

