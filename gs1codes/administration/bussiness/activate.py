from administration.bussiness.models import PrefixRegistry, ResponseGetRegistry, GtinVerified, BrandName, NetContent, TradeItemDescription, TradeItemImageUrl, TransferProcess, CodesVerified, ListGtins
import requests, simplejson, json
from administration.models import Code, Prefix, Enterprise
from administration.common.constants import ProductTypeCodes, ProducState
from typing import TypedDict, List
import simplejson

# Variables URL Activate --------------------------------------------------------
# Url Api Test/Local
urlApi = "http://127.0.0.1:5000"
language = "es-CO"

# Url Api Prod
# urlApi = "https://activatetest.azurewebsites.net";
# -------------------------------------------------------------------------------

# Métodos Registry
def AddLicenseBatch(lpref: List[PrefixRegistry]):
    urlPost = urlApi + "/Registry/BatchMethods/AddLicenses"
    headers = {'Content-type': 'application/json'}
    json_obj = simplejson.dumps(lpref)

    rest_response = requests.post(urlPost, headers = headers, json = lpref)
    
    if rest_response.status_code == 202 or rest_response.status_code == 200:
        res= rest_response.content
        my_json = res.decode('utf8').replace("'", '"')
        resp = json.loads(my_json)
        resp = ""
    else:
        resp = "Error en el servicio al intentar crear la licensia del prefijo. Método: AddLicenses. Error: " + str(rest_response.reason)
   
    # rta2 = JsonConvert.DeserializeObject(rta);
    return resp


def AddLicense(pref: PrefixRegistry):
    
    urlPost = urlApi + "/Registry/SinlgeMethods/AddLicense"
    headers = {'Content-type': 'application/json'}
    #json_obj = simplejson.dumps(pref)

    rest_response = requests.post(urlPost, headers = headers, json = pref)
   
    if (rest_response.status_code == 202 or rest_response.status_code == 200):
        res= rest_response.content
        my_json = res.decode('utf8').replace("'", '"')
        resp = json.loads(my_json)
        resp = ""
    else:
        resp = "Error en el servicio al intentar crear la licensia del prefijo. Método: AddLicense. Error: " + str(rest_response.reason)
    
    return resp

def GetLicense(pref: str):
    
    url = urlApi + "/Registry/SinlgeMethods/GetLicense/" + pref
    rest_response = requests.get(url)
   
    if (rest_response.status_code == 202 or rest_response.status_code == 200):
        resp = rest_response.content
    else:
        resp = str(None)
    
    rta = json.loads(resp)
    return rta

# Métodos Verified
def AddGtinsBatch(listGtins: List[GtinVerified]):
    url = urlApi + "/Verified/BatchMethods/CreateGtins"
    json_obj = simplejson.dumps(listGtins)

    rest_response = requests.post(url, json=listGtins)
   
    if (rest_response.status_code == 202 or rest_response.status_code == 200):
        resp = rest_response.content
    else:
        resp = str(None)
    
    return resp

def VerifiedGs1(okCodes: List[CodesVerified]):
    listGtins = []

    for codes in okCodes:
        obj_code: Code = Code.objects.filter(id=codes['Codes']).first()
        
        if not obj_code:
            pass

        if (obj_code.product_type_id == ProductTypeCodes.Producto.value and obj_code.product_state_id == ProducState.Acitvo_Publicado.value):
            
            obj_prefix: Prefix = Prefix.objects.filter(id=obj_code.prefix_id).first()
            obj_enterprise: Enterprise = Enterprise.objects.filter(id=obj_prefix.enterprise_id).first()

            obj_license: ResponseGetRegistry = GetLicense(str(obj_prefix.id_prefix))

            if (obj_license['status'] == 0):
                obj_registry = PrefixRegistry()
                obj_registry.Key = obj_prefix.id_prefix
                obj_registry.Type = "gcp"
                obj_registry.CompanyName = obj_enterprise.enterprise_name
                obj_registry.Status = 1

                AddPrefRegistry = AddLicense(obj_registry)

            obj_brand = BrandName()
            obj_brand['lang'] = language
            obj_brand['value'] = str(obj_code.brand_id)

            obj_net_content = NetContent()
            obj_net_content['quantity'] = int(obj_code.quantity_code)
            obj_net_content['measurementUnitCode'] = str(obj_code.measure_unit_id)

            targetMarketCountryCode = []
            targetMarketCountryCode.append(str(obj_code.target_market_id))

            obj_trade_item = TradeItemDescription()
            obj_trade_item['lang'] = language
            obj_trade_item['value'] = obj_code.description

            obj_trade_image = TradeItemImageUrl()
            obj_trade_image['lang'] = language
            obj_trade_image['value'] = obj_code.url

            obj_gtin = GtinVerified()

            obj_gtin['gtin'] = str(obj_code.id).zfill(14)

            lista = []
            lista.append(obj_brand)
            obj_gtin['brandname'] =  lista
            obj_gtin['gpcCode'] = str(obj_code.gpc_category_id)
            
            lista = []
            lista.append(obj_net_content)
            obj_gtin['netContent'] = lista
            obj_gtin['status'] = "ACTIVE"
            obj_gtin['targetMarketCountryCode'] = targetMarketCountryCode

            lista = []
            lista.append(obj_trade_item)
            obj_gtin['tradeItemDescription'] = lista

            if (obj_trade_image['value'] != "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg"):
                lista = []
                lista.append(obj_trade_item)
                obj_gtin['tradeItemImageUrl'] = lista
            
            listGtins.append(obj_gtin)
            obj_gtin = None
    
    lista_gtins = ListGtins()
    lista_gtins['listGtins'] = listGtins
    rta = AddGtinsBatch(lista_gtins)

    return rta
