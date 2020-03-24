from django.http import HttpResponse, JsonResponse
from administration.models import Brand, GpcCategory,ProductType
from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
# Import para permisos Staff
# from django.contrib.admin.views.decorators import staff_member_required
import pandas as pd
from administration.bussiness import codes as mcodes
import json

@login_required
def report(request):
    br = Brand.objects.all()
    pt = ProductType.objects.all()
    gtin14s = mcodes.getGtin14byNit('10203040').values.tolist()
    context = {
        "brand_list": br,
        "pt_list": pt,
        "gtin14s_list": gtin14s
        }
    print(br)
    print(request.user.email)
    return render(request, 
                  'administration/frontTemplates/report.html'
                  , context)
# Permisos Staff
# report = staff_member_required(report)