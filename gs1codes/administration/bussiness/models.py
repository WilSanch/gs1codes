from typing import TypedDict, List
from administration.common.constants import CodeType, SchemaCodes, PrefixRangeType, TransferProcess, ProductType
from datetime import datetime
from enum import Enum

class MarkedCode(TypedDict):
    """
    Diccionario de propiedades de un codigo a marcar.
    """
    Codigo: int
    Prefix: int
    Descripcion: str
    TipoProducto: int
    Brand: str
    TargetMarket: str
    Gpc: str
    Textil: str
    Url: str
    State: int
    MeasureUnit: int
    Quantity: float

class MarkData(TypedDict):
    """
    Diccionario para la marcacion de un codigo.
    """
    Nit: str
    Username: str
    TipoProducto: int
    Esquemas: List[int]
    Codigos: List[MarkedCode]

class CodeRespose(TypedDict):
    """
    Diccionario con codigos marcados
    """
    Id: int
    Codigo: int
    
class MarkCodeRespose(TypedDict):
    """
    Diccionario de respuesta para la marcacion de codigos
    """
    IdCodigos: List[CodeRespose]
    MensajeUI: str
    Respuesta: int
    
class MarkCodeGroupbyType(TypedDict):
    TotalVariableWeight : int
    TotalCodesMark: int
    TotalNonVariableWeight: int
    
class ListPrefix(TypedDict):
    Prefix: int
    Codes: List[int]

class RequestCodes(TypedDict):
    '''
    Objeto con cantidad de codigos manuales ,automaticos y con prefijo en la peticion de marcacion
    '''
    Auto: List[int]
    Manual: List[int]
    Prefix : List[ListPrefix]

class PrefixId(TypedDict):
    Id: int
    Range: int

class ActivationInactivationBM(TypedDict):
    Prefixes: PrefixId
    Observation: str
    AssignmentDate: None

class CodeAssignmentRequest(TypedDict):
    Nit: str
    BusinessName: str
    Schema: SchemaCodes
    Quantity: int
    Type: CodeType
    PreferIndicatedPrefix: bool
    PrefixType: PrefixRangeType
    VariedFixedUse: bool
    ScalePrefixes: bool

class CodeAssignation(TypedDict):
    AgreementName: str
    IdAgreement: int
    Request: CodeAssignmentRequest
    UserName: str

class RequestMarkCode(TypedDict):
    Code: int
    Msj: str
    Row: List[object]
    
class DescriptionGtin(TypedDict):
    GlnName: str
    ProdName: str

class ReplyVerify(TypedDict):
    Msj: str
    Validate: bool
    
class ReplyMarCode(TypedDict):
    Codes: List[object]
    Df: object

class RegroupBM(TypedDict):
    Nit: str
    Prefixes: List[PrefixId]
    ContractMigrationDate: datetime

class CodeTransfer(TypedDict):
    OriginNit: str
    DestinationNit: str
    Process: TransferProcess
    Prefixes: List[PrefixId]
    Observation: str

class PrefixRefund(TypedDict):
    Prefixes: PrefixId
    nit: str
    Observation: str

class Gtin14AsignacionRequest(TypedDict):
    idGtin13: int
    idGtin14: int
    descripcion: str
    cantidad: int
    nit: str
    
class listGtin13(TypedDict):
    gtin13s: List[int]
    
class responseValidateExcel(TypedDict):
    valid: bool
    msj: str
    data: object

class Prefix_Validate(TypedDict):
    id : int
    code_quantity_reserved : int
    code_residue : int

# Registry models ---------------------------------------------------------

class PrefixRegistry(TypedDict):
    key: str
    type: str
    companyName: str
    status: int

class ResponseGetRegistry(TypedDict):
    Key: str
    Type: str
    Status: int
    CompanyName: str
    IssuerGLN: str
    LicenseeGLN: str
    DataSourceGLN: str

# Verified models ---------------------------------------------------------
class BrandName(TypedDict):
    Lang: str
    Value: str

class NetContent(TypedDict):
    Quantity: float
    MeasurementUnitCode: str

class TradeItemDescription(TypedDict):
    Lang: str
    Value: str

class TradeItemImageUrl(TypedDict):
    Lang: str
    Value: str

class CodesVerified(TypedDict):
    Codes: str

class GtinVerified(TypedDict):
    Gtin: str
    BrandName: List[BrandName]
    GpcCode: str
    NetContent: List[NetContent]
    Status: str
    TargetMarketCountryCode: List[str]
    TradeItemDescription: List[TradeItemDescription]
    TradeItemImageUrl: List[TradeItemImageUrl]

class CodeASCext(TypedDict):
    Brand: str
    GpcCode: str
    Cant: float
    Measure: int
    Target: str
    Url: str

# Update Url Gtin models ---------------------------------------------------------
#class GtinExt(TypedDict):
#    Gtin: float
#    TipoProducto: ProductType
#    Brand: str
#    TargetMarket: str
#    Gpc: str
#    Url: str
#    MeasureUnit: int
#    Quantity: int

#class UpdateUrlGtin(TypedDict):
#    Nit: str
#    Gtins: List[GtinExt]

#class CodigoRespuestaUpdateUrl(Enum):
#    Existoso = "Exitoso"
#    ProblemaDesconocido = "ProblemaDesconocido"

#class UpdateUrlGtinResult(TypedDict):
#    GtinCreados: List[float]
#    GtinActualizados: List[float]
#    Mesagge: str
#    Respuesta: CodigoRespuestaUpdateUrl

# ----------------------------------------------------------------------