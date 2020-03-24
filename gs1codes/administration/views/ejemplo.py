from rest_framework.decorators import api_view
from django.template import loader
from django.http import HttpResponse, HttpRequest
from django.shortcuts import render
from administration.forms import EjemploForm
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required

def ejemplo(request):
    if request.method == "POST":
        form = None
        return redirect(f"/respuesta/{request.POST['nit']}")
    else:
        form = EjemploForm()
    
    print(form)
    return render(request, 'administration/frontTemplates/index.html', {"form": form})

def nit1(request: HttpRequest):
    return render(request,'administration/frontTemplates/nit1.html',{"pk": request.GET["nit"]})