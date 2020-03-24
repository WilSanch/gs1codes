from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.admin.views.decorators import staff_member_required

def Index(request):
    return render(request, 
                  'registration/index.html'
                  , {})
# report = staff_member_required(report)