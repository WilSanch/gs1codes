from typing import TypedDict, List
from django.http import JsonResponse

class MarkedCode(TypedDict):
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
    Nit: str
    Username: str
    TipoProducto: int
    Esquemas: List[int]
    Codigos: List[MarkedCode]
    id: int

class CodeRespose(TypedDict):
    Id: int
    Codigo: int
    
class MarkCodeRespose(TypedDict):
    IdCodigos: List[CodeRespose]
    MensajeUI: str
    Respuesta: int

def mark_codes(marcation: MarkData) -> MarkCodeRespose:
    """Hacemos lo que toca hacer para marcar"""
    return JsonResponse({
        "IdCodigos": [{
            "Id": 1,
            "Codigo": 7007777777
        }],
        "MensajeUI": "Se marcó correctamente",
        "Respuesta": 200
    })