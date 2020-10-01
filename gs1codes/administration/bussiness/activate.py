from administration.bussiness.models import PrefixRegistry, ResponseGetRegistry, GtinVerified, BrandName, NetContent, TradeItemDescription, TradeItemImageUrl, TransferProcess, CodesVerified
import requests, simplejson, json
from administration.models import Code, Prefix, Enterprise
from administration.common.constants import ProductTypeCodes, ProducState
from typing import TypedDict, List

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
    #json_obj = simplejson.dumps(lpref)

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
   
    if (rest_response.status_code == "202" or rest_response.status_code == "200"):
        resp = rest_response.content
    else:
        resp = str(None)
    
    rta = json.loads(resp)
    return rta

# Métodos Verified
def AddGtinsBatch(lcode: List[GtinVerified]):
    url = urlApi + "/Verified/BatchMethods/CreateGtins"
    #json_obj = simplejson.dumps(lcode)

    rest_response = requests.post(url, json=lcode)
   
    if (rest_response.status_code == "202" or rest_response.status_code == "200"):
        resp = rest_response.content
    else:
        resp = str(None)
    
    return resp

def VerifiedGs1(okCodes: List[CodesVerified]):
    listGtins = []

    for codes in okCodes:
        obj_code: Code = Code.objects.filter(id_prefix=codes.Codes).first()
        
        if not obj_code:
            pass

        if (obj_code.product_type == ProductTypeCodes.Producto.value and obj_code.product_state == ProducState.Acitvo_Publicado.value):
            
            obj_prefix: Prefix = Prefix.objects.filter(id=obj_code.prefix_id).first()
            obj_enterprise: Enterprise = Enterprise.objects.filter(id=obj_prefix.enterprise_id).first()

            obj_license: ResponseGetRegistry = GetLicense(obj_prefix.id_prefix)

            if (obj_license.Status == 0):
                obj_registry = PrefixRegistry()
                obj_registry.Key = obj_prefix.id_prefix
                obj_registry.Type = "gcp"
                obj_registry.CompanyName = obj_enterprise.enterprise_name
                obj_registry.Status = 1

                AddPrefRegistry = AddLicense(obj_registry)

            obj_brand = BrandName()
            obj_brand.Lang = language
            obj_brand.Value = obj_code.brand

            obj_net_content = NetContent()
            obj_net_content.Quantity = obj_code.quantity_code
            obj_net_content.MeasurementUnitCode = obj_code.measure_unit

            targetMarketCountryCode = obj_code.target_market

            obj_trade_item = TradeItemDescription()
            obj_trade_item.Lang = language
            obj_trade_item.Value = obj_code.description

            obj_trade_image = TradeItemImageUrl()
            obj_trade_image.Lang = language
            obj_trade_image.Value = obj_code.url

            obj_gtin = GtinVerified()

            obj_gtin.Gtin = str(obj_code.id).zfill(14)
            obj_gtin.BrandName = list(obj_brand)
            obj_gtin.GpcCode = obj_code.gpc_category
            obj_gtin.NetContent = list(obj_net_content)
            obj_gtin.Status = "ACTIVE"
            obj_gtin.TargetMarketCountryCode = list(targetMarketCountryCode)
            obj_gtin.TradeItemDescription = list(obj_trade_item)

            if (obj_trade_image.Value != "https://bloblogycacolabora.blob.core.windows.net/imagecontainer/ImagenNoDisponible.jpg"):
                obj_gtin.tradeItemImageUrl = list(obj_trade_image)
            
            listGtins.append(obj_gtin)
            obj_gtin = None
    
    rta = AddGtinsBatch(listGtins)

    return rta
