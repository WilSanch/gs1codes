from enum import Enum
import pandas as pd
class StateCodes():
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

class States():
    Disponible = 1
    Asignado = 2
    Suspendido = 3
    Reagrupado = 4
    NoReutilizable = 5
    UsoGS1 = 6
    Reservado_Migracion = 9
    PendienteProceso = 10
    Procesado = 11
    SuspendidoPorReagrupacion = 12
    Cesion = 13
    
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
    
class ProductType(Enum):
    Producto = 1
    Textil = 2
    Farmacéutico = 3
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

def dfCodesOK(data=None):
    return pd.DataFrame(data=data, columns = ColumnsCode)