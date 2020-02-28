from enum import Enum
import pandas as pd
import re
class CodeType(Enum):
    CodigoGtin8Nuevos = 122
    DerechoIdentificacionNuevos = 55600
    DerechoIdentificacionExcenNuevos = 55601
    DerechoIdentificacionPesoVariado = 55602
    DerechoIdentificacionGln = 55603
    DerechoIdentificacionConfeccionTextilCalzado = 55604
    IdentificacionDocumentos = 55800

class SchemaCodes(Enum):
    RenovacionAnual31Diciembre = 1
    Renovacion99Años = 2
    RenovacionAnualSegunFechaActivacion = 3
    Renovacion10Años = 4
    RenovacionVitalicia = 5
    RenovacionAnual31DiciembreGs1 = 6
    Esquema99AñosRVC = 7

class PrefixRangeType(Enum):
    R_4D = 2
    R_5D = 3
    R_6D = 4
    R_7D = 5
    R_8D = 6
    GLN_gratuito = 7
    GLN_vitalicio = 8
    Gtin8 = 11
    PesoVar = 12
    PesoFijo = 13

class UserMessages():
    Tmp1 = "No hay mas prefijos disponibles del tipo de prefijo "
    Tmp2 = "Debe especificar un tipo de prefijo cuando se solicitan codigos GTIN8"
    Tmp3 = "El prefijo es un 8D y por tanto no se puede reagrupar."
    Tmp4 = "El prefijo que se quiere asignar manualmente debe estar en estado DISPONIBLE."
    Tmp5 = "El prefijo no existe."
    Tmp6 = "El prefijo  ya se encuentra asignado a otra empresa."
    Tmp7 = "El prefijo que intenta asignar no es válido. Posibles causas: no existe o no es del tipo indicado."
    Tmp8 = "La empresa no tiene derecho al uso del prefijo indicado o el prefijo no es reagrupable."
    Msg01 = "La empresa para la que se hace la solicitud no existe. NIT: "
    Msg02 = "La cantidad de codigos solicitada debe ser superior a cero."
    Msg03 = "El tipo de esquema no es válido."
    Msg04 ="La disponibilidad de codigos de tipo  ha llegado a su fin. Verifique la informacion de la empresa "
    Msg06 = "La empresa no tiene derecho al uso del prefijo indicado."

class MarkMessages():
    MarkOk = "Gtin Insertado Correctamente"
    MarkNoExist = "Gtin no existe o no esta asociado a la empresa"
    Error01 = "El código no se encuentra ni disponible ni reservado"
    ErrorBrand = "Brand vacia o incorrecta"
    ErrorTargetMarket = "Target Marked incorrecto"
    ErrorGpc = "Categoria GPC incorrecta"
    ErrorTextil = "Categoria Textil incorrecta"
    ErrorAtc = "Categoria ATC incorrecta"
    ErrorQuantity = "Quantity debe ser mayor a 0"
    ErrorMeasureUnit= "MeasureUnit vacia o incorrecta"
    ErrorUrl = "Url invalida o extension de imagen incorrecta"
       
class Gtin14Messages():
    CantDuplicada = "YA EXISTE OTRO GTIN14 PARA EL GTIN13 CON LA MISMA CANTIDAD"
    Gtin14Duplicado = "GTIN14 DUPLICADO"    
    DvGtin14 = "DIGITO DE VERIFICACION DEL GTIN14 ERRONEO"
    Gtin13NotMark = "EL GTIN13 NO SE ENCUENTRA ASIGNADO"
    Gtin14Cant = "CANTIDAD DE CODIGOS MAYOR A 9"
    Gtin14NoEnterprise = "Error Gtin14 no pertenece a la empresa"

class ProductType():
    Producto = 1
    Textil = 2
    Farmaceutico = 3
    Gln = 4
    EANPuntoVenta = 5
    ProductoUnidadEmpaque = 6
    ProductoPesoVariable = 7
    Recaudo = 8
    CD_GLN = 9
    ActivosFijos = 10
    GtinVitalicio = 11
    GlnTransaccional = 12
    CdGlnTransaccional = 13
    ProductoGLN = 14
    FarmaceuticoNoGenerico = 15
    
class StCodes(Enum):
    """state codes"""
    Disponible = 1
    Asignado = 2
    Suspendido = 3
    Reagrupado = 4
    No_Reutilizable = 5
    Uso_GS1 = 6
    Reservado_Migración = 9
    Pendiente_de_proceso = 10
    Procesado = 11
    Suspendido_por_reagrupación_sin_derecho_al_uso = 12
    Cesion = 13
    EN_CONFLICTO = 99
    
class Ranges(Enum):
    Recaudo_Vitalicio_Documentos = 1
    _4_digitos = 2
    _5_digitos = 3
    _6_digitos = 4
    _7_digitos = 5
    _8_digitos = 6
    GLN_gratuito = 7
    GLN_Vitalicio_conectividad = 8
    Plataforma = 9
    GTIN_vitalicio_productos = 10
    Peso_variable = 12
    Peso_variable_peso_fijo = 13
    
class ProductTypeCodes(Enum):
    Producto = 1
    Textil = 2
    Farmaceutico = 3
    GLN = 4
    EAN_Punto_de_venta = 5
    Producto_unidad_de_empaque = 6
    Producto_peso_variable = 7
    Recaudo = 8
    CD_GLN = 9
    Activos_fijos = 10
    GTIN_Vitalicio = 11
    GLN_Transaccional = 12
    CD_GLN_Transaccional = 13
    Producto_GLN = 14
    Farmacéutico_No_Generico = 15

class ProducState(Enum):
    Acitvo_Publicado = 1
    Inactivo = 2
    En_Desarrollo = 3

ColumnsCode = [
    'id',
    'alternate_code',
    'description',
    'assignment_date',
    'url',
    'quantity_code',
    'gln_name',
    'agreement_id',
    'atc_category_id',
    'brand_id',
    'gpc_category_id',
    'measure_unit_id',
    'prefix_id',
    'product_state_id',
    'product_type_id',
    'range_id',
    'state_id',
    'target_market_id',
    'textil_category_id' 
]

ColummnsGtin14Gtin13=[
    'id',
    'id_code',
    'quantity'
]

ColummnsGtin14s=[
    'id',
    'id_code_id',
    'description',
    'quantity'
]

VALID_IMAGE_EXTENSIONS = [
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
]

regexUrl = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

def dfCodesOK(data=None):
    return pd.DataFrame(data=data, columns = ColumnsCode)

def dfCodesGtin14Gtin13(data=None):
    return pd.DataFrame(data=data, columns = ColummnsGtin14Gtin13)

def dfCodesGtin14s(data=None):
    return pd.DataFrame(data=data, columns = ColummnsGtin14s)

def valid_url_extension(url, extension_list=VALID_IMAGE_EXTENSIONS):
    return any([url.endswith(e) for e in extension_list])  