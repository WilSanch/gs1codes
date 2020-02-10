from typing import TypedDict, List
from administration.common.constants import CodeType, SchemaCodes, PrefixRangeType


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
    Atc: str
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

