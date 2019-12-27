import json
from django.http import HttpResponse
from administration.bussiness.codes import mark_codes

def mark(request):
  if request.method == 'POST':
    json_data = json.loads(request.body) # request.raw_post_data w/ Django < 1.4
    
    return mark_codes(json_data)