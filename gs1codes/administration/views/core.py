import json
from django.http import HttpResponse
from administration.bussiness.codes import mark_codes
from administration.bussiness.prefix import activation,Pruebas
from django.http import JsonResponse

def mark(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4
    
    return JsonResponse(mark_codes(json_data))

def activate(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(activation(json_data))

def pruebas(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) 
    
    return JsonResponse(Pruebas(json_data))