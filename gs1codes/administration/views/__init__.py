from .core import mark, get_gpc
from .core import activate, inactivate, assignate, regroup, transfer, refund, update_validity_date
from .core import RegistrarGTIN14, GetGtin14s, ListRegistrarGTIN14, ListGetGtin14s
from .core import ValidateGtinByNit, BuscaGlnNit, GetGlnOnEnterprise, GetGtinByNitAndTypeCode, GetCodigosByEsquema, GetCodigosByNit, SaldosByNit, GetCodigosByTipoProducto
from .ejemplo import ejemplo, nit1
from .ejemplo2 import report
from .PowerBI import reportPowerBI
from .Index import Index
from .prefix import assignation, assignate_search_enterprise, load_code_types, load_prefix_types, load_codes_table, action_prefix, function_2nd_grid, load_prefix_table, update_validity_date_prefix,transfer_prefix,enterprise_modify
from .CarguePortafolio import cargue, procesaBlobs
from .cargueArchivo import cargue_archivo