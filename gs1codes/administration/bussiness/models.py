from typing import TypedDict, List
from administration.common.constants import CodeType, Schema, PrefixRangeType


class MarkedCode(TypedDict):
    """
    Diccionario de propiedades de un codigo a marcar.
    """
    Codigo: int
    Prefix: int
    Descripcion: str
    TipoProducto: List[int]
    Id: int
    Brand: str
    TargetMarket: str
    Gpc: str
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
    id: int

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

class PrefixId(TypedDict):
    Id: str
    Range: int

class ActivationInactivationBM(TypedDict):
    Prefixes: PrefixId
    Observation: str
    AssignmentDate: None


class CodeAssignmentRequest(TypedDict):
    Nit: str
    BusinessName: str
    Schema: Schema
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
