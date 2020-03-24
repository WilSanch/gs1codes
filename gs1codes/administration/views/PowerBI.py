from django.template import RequestContext
from django.shortcuts import render_to_response, render
from django.contrib.auth.decorators import login_required
import requests
import json

@login_required
def reportPowerBI(request):
    url = "https://testpowerbiapi.azurewebsites.net/api/User/PowerBI?WorkspaceId=3c149686-3b16-40be-b187-0bb1df10b31e&ReportId=e054e2de-b991-4205-9cae-38abaff62f60"
    response = requests.get(url)
    res = response.content

    my_json = res.decode('utf8').replace("'", '"')

    data = json.loads(my_json)
    token = data['embedToken']['token']
    rptUrl = data['rptUrl']
    rptId = data['rptId']
    return render(request, 
                  'administration/frontTemplates/powerbi.html'
                  , {"token": token,"rptUrl": rptUrl,"rptId":rptId})
