import collections
import json
import math
import re
import pandas as pd
from django.db import transaction
from typing import TypedDict, List
from datetime import datetime
from django.utils import timezone
from django.db import connection, transaction, IntegrityError
from rest_framework import serializers
from administration.models.temporal import Code as tmpCode
from administration.common.functions import Queries, Common
from administration.bussiness.models import *
from administration.common.constants import *
from administration.models.core import ProductType, GpcCategory, MeasureUnit, Prefix, Range, Code, Country, AtcCategory, TextilCategory, Brand, Code_Gtin14, Enterprise

class ProductTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductType
        fields = '__all__'

class GpcCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GpcCategory
        # fields = ['brick_code','spanish_name_brick']
        fields = '__all__'

class MeasureUnitsSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeasureUnit
        # fields = ['brick_code','spanish_name_brick']
        fields = '__all__'

def get_gpc_category(marcation: MarkData):
    gpc = GpcCategory.objects.all()
    data = {"result": list(gpc.values("id", "spanish_name_brick"))}
    return data

def mark_codes(marcation: MarkData):

    CodiVal = valida_codes(marcation["Codigos"])

    codigosRepetidos = codigosRepetidosfn(CodiVal)

    if(len(codigosRepetidos) >= 1):
        return {
            "IdCodigos": codigosRepetidos,
            "MensajeUI": marcation["Nit"],
            "Respuesta": 'Error Codigos Repetidos'
        }

    TotalMark = TotalMarkCodes(CodiVal)
    AvailableCodesVariableWeight = TotalAviablesCodes(marcation["Nit"], True)
    AvailableCodesNoneVariableWeight = TotalAviablesCodes(
        marcation["Nit"], False)

    if (TotalMark.TotalVariableWeight > AvailableCodesVariableWeight):
        return {
            "IdCodigos": [],
            "MensajeUI": 'Error Saldos',
            "Respuesta": 'Esta tratando de marcar {} codigos de pesovariable y dispone de {}'.format(TotalMark.TotalVariableWeight, AvailableCodesVariableWeight)
        }

    if (TotalMark.TotalNonVariableWeight > AvailableCodesNoneVariableWeight):
        return {
            "IdCodigos": [],
            "MensajeUI": 'Error Saldos',
            "Respuesta": 'Esta tratando de marcar {} codigos y dispone de {}'.format(TotalMark.TotalNonVariableWeight, AvailableCodesNoneVariableWeight)
        }

    dfcodesMark = pd.DataFrame(data=CodiVal)
    dfcodesMark[['Codigo', 'Prefix']] = dfcodesMark[[
        'Codigo', 'Prefix']].astype(float)
    dfcodesMarkGroup = dfcodesMark.groupby('TipoProducto')

    # se retonara el Df con los codigos OK y el resumen de la validacion de los codigos.
    replyMarCode = Mark_Codes_fn(dfcodesMarkGroup, marcation['Nit'])
    # print(replyMarCode.Df)
    ReplyUpdate = UpdateCodes(replyMarCode.Df)

    CodOk = 0
    CodError = 0
    for rta in replyMarCode.Codes:
        if rta['Msj'] == MarkMessages.MarkOk:
            CodOk = CodOk + 1
        else:
            CodError = CodError + 1

    print('Codigos Marcados Correctamente: ' +
          str(CodOk) + 'Con Errores: ' + str(CodError))

    return {
        "IdCodigos": replyMarCode.Codes,
        "Respuesta": 'InsertOK',
        "MensajeUI": 'Codigos Marcados Correctamente : ' + str(CodOk) + ' Con Errores: ' + str(CodError)
    }

@transaction.atomic
def UpdateCodes(df):
    try:
        cur = connection.cursor()
        q1 = Queries.createCodeTemp()
        cur.execute(q1)
        tmpCode.objects.bulk_create(Code(**vals) for vals in df.to_dict('records'))
        q2 = Queries.upsertCode()
        cur.execute(q2)
        return 'InsertOK'
    except Exception as ex:
        return ex

def codigosRepetidosfn(codigos):
    df = pd.DataFrame(data=codigos)
    rep = df.groupby(['Codigo']).count()
    repetidos = rep[rep.Descripcion == 2]
    msgs = "El código " + repetidos.index.astype(
        "str") + " tiene " + repetidos.Descripcion.astype("str") + " repeticiones"
    return msgs.to_list()

def TotalMarkCodes(codigos):
    dfcodesMark = pd.DataFrame(data=codigos)
    dfcodesMarkGroup = dfcodesMark.groupby('TipoProducto')
    markCodeGroupbyType = MarkCodeGroupbyType
    pv = 0

    for c in codigos:
        if(c['TipoProducto'] == ProductTypeCodes.Producto_peso_variable.value):
            pv = pv+1

    if pv > 0:
        markCodeGroupbyType.TotalVariableWeight = dfcodesMarkGroup.get_group(
            ProductTypeCodes.Producto_peso_variable.value)['Descripcion'].count()
    else:
        markCodeGroupbyType.TotalVariableWeight = 0

    markCodeGroupbyType.TotalCodesMark = len(codigos)
    markCodeGroupbyType.TotalNonVariableWeight = markCodeGroupbyType.TotalCodesMark - \
        markCodeGroupbyType.TotalVariableWeight
    return markCodeGroupbyType

def TotalAviablesCodes(Nit, VariableWeight):
    q1 = Queries.AvailableCodes(Nit, VariableWeight)
    cursor = connection.cursor()
    cursor.execute(q1)
    spv = cursor.fetchone()
    return spv[0]

def ChangeTypeGlnGtin(CodObj, Description):
    '''
    Cambios de Descripcion para GTIN tipo Producto_GLN
    '''
    descriptionGtin = DescriptionGtin
    glnName = ''
    prodName = ''
    if (CodObj['product_type_id'].tolist()[0] == ProductTypeCodes.Producto.value
        or CodObj['product_type_id'].tolist()[0] == ProductTypeCodes.Textil.value
            or CodObj['product_type_id'].tolist()[0] == ProductTypeCodes.Farmaceutico.value):
        prodName = CodObj['description'].tolist()[0]
        glnName = Description

    if (CodObj['product_type_id'].tolist()[0] == ProductTypeCodes.GLN.value
            or CodObj['product_type_id'].tolist()[0] == ProductTypeCodes.EAN_Punto_de_venta.value):
        glnName = CodObj['description'].tolist()[0]
        prodName = Description

    descriptionGtin.GlnName = glnName
    descriptionGtin.ProdName = prodName

    return descriptionGtin

def ValidateVerified(row):
    '''
    Validacion de Campos verified
    '''
    rv = ReplyVerify
    rv.Msj = "Ok"
    rv.Validate = True

    if len(row['Brand']) <= 0:
        rv.Msj = MarkMessages.ErrorBrand
        rv.Validate = False
    else:
        if Brand.objects.filter(name=row['Brand']).count() <= 0:
            brand = Brand()
            brand.name = row['Brand']
            brand.save()

    if Country.objects.filter(iso_a3=row['TargetMarket']).count() <= 0:
        rv.Msj = MarkMessages.ErrorTargetMarket
        rv.Validate = False
        return rv

    if row['TipoProducto'] == ProductTypeCodes.Producto.value:
        if GpcCategory.objects.filter(brick_code=row['Gpc']).count() <= 0:
            rv.Msj = MarkMessages.ErrorGpc
            rv.Validate = False
            return rv

    if row['TipoProducto'] == ProductTypeCodes.Textil.value:
        if TextilCategory.objects.filter(code=row['Textil']).count() <= 0:
            rv.Msj = MarkMessages.ErrorTextil
            rv.Validate = False
            return rv
        if GpcCategory.objects.filter(brick_code=row['Gpc']).count() <= 0:
            rv.Msj = MarkMessages.ErrorGpc
            rv.Validate = False
            return rv

    if row['TipoProducto'] == ProductTypeCodes.Farmaceutico.value:
        if AtcCategory.objects.filter(code=row['Gpc']).count() <= 0:
            rv.Msj = MarkMessages.ErrorAtc
            rv.Validate = False
            return rv

    if row['Quantity'] <= 0:
        rv.Msj = MarkMessages.ErrorQuantity
        rv.Validate = False
        return rv

    if MeasureUnit.objects.filter(id=row['MeasureUnit']).count() <= 0:
        rv.Msj = MarkMessages.ErrorMeasureUnit
        rv.Validate = False
        return rv

    if (re.match(regexUrl, row['Url']) is not None):
        url = valid_url_extension(row['Url'], VALID_IMAGE_EXTENSIONS)
    else:
        url = False

    if url == False:
        rv.Msj = MarkMessages.ErrorUrl
        rv.Validate = False
        return rv

    return rv

def Mark_Code_fn(Code, Nit, row):
    '''
    Validacion de datos para creacion del ROW a insertar en el DF
    Return: Row listo para insertar en el DF
    '''
    rm = RequestMarkCode
    q1 = Queries.codObj(Code, Nit)
    cursor = connection.cursor()
    cursor.execute(q1)
    CodObj = dfCodesOK(data=cursor.fetchall())

    if (len(CodObj) <= 0):
        rm.Code = Code
        rm.Msj = MarkMessages.MarkNoExist
        rm.Row = None
        return rm

    if (CodObj['state_id'].tolist()[0] != StCodes.Disponible.value) and \
       (CodObj['state_id'].tolist()[0] != StCodes.Reservado_Migración.value):
        print('Asignado')
        if (row['TipoProducto'] == ProductTypeCodes.Producto_GLN.value) \
                and (CodObj['product_state_id'].tolist()[0] == ProducState.En_Desarrollo.value):
            # Creacion de Producto_GLN
            descriptionGtin: DescriptionGtin = ChangeTypeGlnGtin(
                CodObj, row['Descripcion'])
            CodObj.at[0, 'description'] = descriptionGtin.ProdName
            CodObj.at[0, 'gln_name'] = descriptionGtin.GlnName
            CodObj.at[0, 'product_type_id'] = ProductTypeCodes.Producto_GLN.value
            CodObj.at[0, 'assignment_date'] = timezone.now()
            rm.Code = Code
            rm.Msj = MarkMessages.MarkOk
            rm.Row = CodObj.values.tolist()
            return rm
        else:
            rm.Code = Code
            rm.Msj = MarkMessages.Error01
            rm.Row = None
            return rm
    else:
        if (row['TipoProducto'] == ProductTypeCodes.Producto.value or
            row['TipoProducto'] == ProductTypeCodes.Textil.value or
                row['TipoProducto'] == ProductTypeCodes.Farmaceutico.value):
            # validacion verified
            validateVerified = ValidateVerified(row)
            if validateVerified.Validate == True:
                CodObj.at[0, 'description'] = row['Descripcion']
                CodObj.at[0, 'assignment_date'] = timezone.now()
                CodObj.at[0, 'url'] = row['Url']
                CodObj.at[0, 'quantity_code'] = row['Quantity']
                CodObj.at[0, 'brand_id'] = Brand.objects.filter(name=row['Brand'])[
                    0].id
                if row['TipoProducto'] == ProductTypeCodes.Producto.value:
                    CodObj.at[0, 'gpc_category_id'] = GpcCategory.objects.filter(
                        brick_code=row['Gpc'])[0].id
                if row['TipoProducto'] == ProductTypeCodes.Textil.value:
                    CodObj.at[0, 'gpc_category_id'] = GpcCategory.objects.filter(
                        brick_code=row['Gpc'])[0].id
                    CodObj.at[0, 'textil_category_id'] = TextilCategory.objects.filter(
                        code=row['Textil'])[0].id
                if row['TipoProducto'] == ProductTypeCodes.Farmaceutico.value:
                    CodObj.at[0, 'atc_category_id'] = AtcCategory.objects.filter(code=row['Gpc'])[
                        0].id
                CodObj.at[0, 'measure_unit_id'] = MeasureUnit.objects.filter(
                    id=row['MeasureUnit'])[0].id
                CodObj.at[0, 'product_state_id'] = row['State']
                CodObj.at[0, 'product_type_id'] = row['TipoProducto']
                CodObj.at[0, 'state_id'] = StCodes.Asignado.value
                CodObj.at[0, 'target_market_id'] = Country.objects.filter(
                    iso_a3=row['TargetMarket'])[0].iso_n3
                rm.Code = Code
                rm.Msj = MarkMessages.MarkOk
                rm.Row = CodObj.values.tolist()
                return rm
            else:
                rm.Code = Code
                rm.Msj = validateVerified.Msj
                rm.Row = None
                return rm
        else:
            CodObj.at[0, 'state_id'] = StCodes.Asignado.value
            CodObj.at[0, 'description'] = row['Descripcion']
            CodObj.at[0, 'assignment_date'] = timezone.now()
            CodObj.at[0, 'product_type_id'] = row['TipoProducto']
            rm.Code = Code
            rm.Msj = MarkMessages.MarkOk
            rm.Row = CodObj.values.tolist()
            return rm

def Mark_Codes_fn(dfg, Nit):
    '''
    Creacion del DF dependiento el tipo de marcacion para realizar el UPDATE de la tabla Codes
    '''
    replyMarCode = ReplyMarCode
    rCodes = []
    dfCodes = dfCodesOK()
    for TipoProducto, Codigo in dfg:
        rc = MarkedCodesfn(Codigo, Nit, TipoProducto)
        for row_index, row in Codigo.iterrows():
            if (not math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
                # AsignacionManual
                Code = rc.Manual.pop()
                Cod = Mark_Code_fn(Code, Nit, row)
                if not (Cod.Row == None):
                    dfCodes.loc[len(dfCodes.index)] = Cod.Row[0]
                    rCodes.append(
                        {"Cod": Cod.Code, "Desc": row['Descripcion'], "Msj": Cod.Msj})
                else:
                    rCodes.append(
                        {"Cod": Cod.Code, "Desc": row['Descripcion'], "Msj": Cod.Msj})
            if (math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
                # AsignacionAuto
                Code = rc.Auto.pop()
                Cod = Mark_Code_fn(Code, Nit, row)
                if not (Cod.Row == None):
                    dfCodes.loc[len(dfCodes.index)] = Cod.Row[0]
                    rCodes.append(
                        {"Cod": Cod.Code, "Desc": row['Descripcion'], "Msj": Cod.Msj})
                else:
                    rCodes.append({
                        "Cod": Cod.Code, "Desc": row['Descripcion'], "Msj": Cod.Msj})
            if (not math.isnan(row['Prefix'])) and (math.isnan(row['Codigo'])):
                # AsignacionPrefijo
                pr = row['Prefix']
                for prefix in rc.Prefix:
                    prc = prefix['Prefix']
                    if prc == pr:
                        Code = prefix['Codes'].pop()
                        Cod = Mark_Code_fn(Code, Nit, row)
                        if not (Cod.Row == None):
                            dfCodes.loc[len(dfCodes.index)] = Cod.Row[0]
                            rCodes.append(
                                {"Cod": Cod.Code, "Desc": row['Descripcion'], "Msj": Cod.Msj})
                        else:
                            rCodes.append({"Cod": Cod.Code, "Msj": Cod.Msj})

    # debo retornar el df con los codigos OK
    replyMarCode.Codes = rCodes
    replyMarCode.Df = dfCodes
    return replyMarCode

def MarkedCodesfn(df, Nit, TipoProducto):
    '''
    Se obtienen codigos manuales ,automaticos y con prefijo de la peticion de marcacion disponibles en la DB
    '''
    rc = RequestCodes
    rc.Auto = []
    rc.Manual = []
    rc.Prefix = []
    auto = 0
    codManuales = []
    CodAuto = []
    Prefix = []
    codPref = []
    strPref = ''
    for row_index, row in df.iterrows():
        if (not math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            codManuales.append(row['Codigo'])

        if (math.isnan(row['Codigo'])) and (math.isnan(row['Prefix'])):
            auto = auto + 1

        if (not math.isnan(row['Prefix'])) and (math.isnan(row['Codigo'])):
            Prefix.append(row['Prefix'])

    CodManual = str(',').join([str(i) for i in codManuales])
    prefixGrouped = collections.Counter(Prefix)

    pv = False
    if (TipoProducto == ProductTypeCodes.Producto_peso_variable.value):
        pv = True

    if (len(codManuales) > 0):
        q1 = Queries.MarkingCodesManual(CodManual, Nit, pv, len(codManuales))
        cursor = connection.cursor()
        cursor.execute(q1)
        dpcd = pd.DataFrame(cursor.fetchall(), columns=['id'])
        CodDips = dpcd['id'].tolist()
        rc.Manual = codManuales
        rc.Auto = CodDips

    if (len(Prefix) > 0):
        for p, c in prefixGrouped.items():
            # print(p,':',c)
            q1 = Queries.MarkingCodesPrefix(Nit, pv, CodManual, p, c)
            cursor = connection.cursor()
            cursor.execute(q1)
            dpcd = pd.DataFrame(cursor.fetchall(), columns=['id'])
            CodDips = dpcd['id'].tolist()
            # Corregir
            rc.Prefix.append({
                "Prefix": p,
                "Codes": CodDips})
            codPref.append(CodDips)
        strPref = str(',').join([str(i) for i in codPref])

    if (auto > 0):
        q1 = Queries.MarkingCodesAuto(Nit, pv, strPref.replace(
            '[', '').replace(']', ''), CodManual, auto)
        cursor = connection.cursor()
        cursor.execute(q1)
        dpcd = pd.DataFrame(cursor.fetchall(), columns=['id'])
        CodDips = dpcd['id'].tolist()
        rc.Auto = CodDips

    return rc

def valida_ver(code: MarkedCode):

    if('Gpc' not in code):
        code['Gpc'] = None

    if('MeasureUnit' not in code):
        code['MeasureUnit'] = None
        print('MeasureUnit Vacio: ' + str(code['Codigo']))

    mu = MeasureUnit.objects.filter(id=code['MeasureUnit']).count()
    if (mu > 0):
        gpc = GpcCategory.objects.filter(brick_code=code['Gpc']).count()
        if (gpc > 0):
            return True
        else:
            return 'No existe categoria GPC'
    else:
        return 'No existe unidad de medida'

def valida_codes(codes):
    '''
    Validacion del JSON recibido en la peticion de marcacion
    '''
    for code in codes:
        if('Codigo' not in code):
            code['Codigo'] = None

        if('Prefix' not in code):
            code['Prefix'] = None

        if('Descripcion' not in code):
            code['Descripcion'] = None

        if('TipoProducto' not in code):
            code['TipoProducto'] = None

        if('Brand' not in code):
            code['Brand'] = ''

        if('TargetMarket' not in code):
            code['TargetMarket'] = None

        if('Gpc' not in code):
            code['Gpc'] = None

        if('Textil' not in code):
            code['Textil'] = None

        if('Url' not in code):
            code['Url'] = None

        if('State' not in code):
            code['State'] = ProducState.En_Desarrollo.value

        if('MeasureUnit' not in code):
            code['MeasureUnit'] = 0

        if('Quantity' not in code):
            code['Quantity'] = 0

    return codes

def code_assignment(prefix, ac: CodeAssignmentRequest, username, range_prefix, enterprise, existing_prefix):
    try:

        product_type: int = None
        bulk_code = []

        if (ac.Type == CodeType.CodigoGtin8Nuevos):
            product_type = ProductType.Producto.value

        if (ac.Type == CodeType.DerechoIdentificacionGln):
            product_type = ProductType.GLN.value

        if (ac.Type == CodeType.IdentificacionDocumentos):
            product_type = ProductType.Recaudo.value

        if (not existing_prefix):
            code_list = Common.CodeGenerator(
                prefix.id_prefix, prefix.range_id, ac.Quantity)
        else:
            code_list = Common.CodeGenerator(
                existing_prefix.id_prefix, existing_prefix.range_id, enterprise.code_residue)

            for code in code_list:
                new_code = Code()
                new_code.id = code
                new_code.assignment_date = timezone.now()
                new_code.prefix_id = existing_prefix.id
                new_code.state_id = StCodes.Asignado.value
                new_code.product_type_id = product_type
                bulk_code.append(new_code)

            code_list = Common.CodeGenerator(
                prefix.id_prefix, prefix.range_id, ac.Quantity - enterprise.code_residue)

        for code in code_list:
            new_code = Code()
            new_code.id = code
            new_code.assignment_date = timezone.now()
            new_code.prefix_id = prefix.id
            new_code.state_id = StCodes.Asignado.value
            bulk_code.append(new_code)

        with transaction.atomic():
            Code.objects.bulk_create(bulk_code)

        return ""
    except Exception as ex:
        return "No fue posible insertar los códigos."

def RegistryGtin14(gtin14AsignacionRequest: Gtin14AsignacionRequest):
    '''
    Registra in Gtin14 basesandose en la reglas establecidas por el estandar.
    '''
    idEnterprise = Enterprise.objects.filter(
        identification=gtin14AsignacionRequest['nit'])[0].id
    GTIN14_SINESQUEMA = Common.CalculaDV(str(gtin14AsignacionRequest['idGtin14'])[
                                         1:len(str(gtin14AsignacionRequest['idGtin14'])) - 1])
    valGtin14 = validaGtin14(GTIN14_SINESQUEMA, idEnterprise)

    if valGtin14 == 1:
        q1 = Queries.GetGtin14byGtin13(gtin14AsignacionRequest['idGtin13'])
        cursor = connection.cursor()
        cursor.execute(q1)
        Gtin14Gtin13 = dfCodesGtin14Gtin13(data=cursor.fetchall())
        if len(Gtin14Gtin13) < 9:
            cantGtin14 = Gtin14Gtin13[Gtin14Gtin13['quantity']
                                      == gtin14AsignacionRequest['cantidad']]
            if len(cantGtin14) == 1:
                return {"Response": Gtin14Messages.CantDuplicada}
            else:
                DupGtin14 = Gtin14Gtin13[Gtin14Gtin13['id']
                                         == gtin14AsignacionRequest['idGtin14']]
                if len(DupGtin14) == 1:
                    return {"Response": Gtin14Messages.Gtin14Duplicado}
                else:
                    MarkedGtin13 = Code.objects.filter(id=gtin14AsignacionRequest['idGtin13']).filter(
                        state_id=StCodes.Asignado.value).count()
                    if MarkedGtin13 == 1:
                        DvGtin14 = Common.CalculaDV(str(gtin14AsignacionRequest['idGtin14'])[
                                                    :len(str(gtin14AsignacionRequest['idGtin14'])) - 1])
                        if DvGtin14 == str(gtin14AsignacionRequest['idGtin14']):
                            gtin14 = Code_Gtin14()
                            gtin14.id = gtin14AsignacionRequest['idGtin14']
                            gtin14.id_code_id = gtin14AsignacionRequest['idGtin13']
                            gtin14.description = gtin14AsignacionRequest['descripcion']
                            gtin14.quantity = gtin14AsignacionRequest['cantidad']
                            gtin14.state_id = StCodes.Asignado.value
                            gtin14.save()
                            return {"Response": gtin14AsignacionRequest['idGtin14']}
                        else:
                            return {"Response": Gtin14Messages.DvGtin14}
                    else:
                        return {"Response": Gtin14Messages.Gtin13NotMark}
        else:
            return {"Response": Gtin14Messages.Gtin14Cant}
    else:
        return {"Response": Gtin14Messages.Gtin14NoEnterprise}

def validaGtin14(GTIN14_SINESQUEMA, idEnterprise):
    q1 = Queries.validateGtin14(GTIN14_SINESQUEMA, idEnterprise)
    cursor = connection.cursor()
    cursor.execute(q1)
    ExisteGtin = cursor.fetchone()
    return ExisteGtin[0]

def GetGtin14sbyGtin13(gtinBase):
    q1 = Queries.GetGetin14s(gtinBase)
    cursor = connection.cursor()
    cursor.execute(q1)
    Gtin14Gtin13 = dfCodesGtin14s(data=cursor.fetchall())
    Gtin14DataBM = {}
    Gtin14DataBM['Codigos'] = []
    for row_index, row in Gtin14Gtin13.iterrows():
        Gtin14DataBM['Codigos'].append(
            {
                "IdGtin14": row['id'],
                "IdGtinBase": row['id_code_id'],
                "Descripcion": row['description'],
                "Cantidad": row['quantity']
            }
        )
    return Gtin14DataBM

def ListGetGtin14sGtin13(ListGtin13: listGtin13):
    CodGtin13s = str(',').join([str(i) for i in ListGtin13['ListGtin13']])
    q1 = Queries.GetGetin14sList(CodGtin13s)
    cursor = connection.cursor()
    cursor.execute(q1)
    Gtin14Gtin13 = dfCodesGtin14s(data=cursor.fetchall())
    Gtin14DataBM = {}
    Gtin14DataBM['Codigos'] = []
    for row_index, row in Gtin14Gtin13.iterrows():
        Gtin14DataBM['Codigos'].append(
            {
                "IdGtin14": row['id'],
                "IdGtinBase": row['id_code_id'],
                "Descripcion": row['description'],
                "Cantidad": row['quantity']
            }
        )
    return Gtin14DataBM

def ListRegistryGTIN14(request: List[Gtin14AsignacionRequest]):
    json = {}
    json['Request'] = []
    for gtin14 in request:
        res = RegistryGtin14(gtin14)
        json['Request'].append(res)
    return json

def getGtin14byNit(Nit):
    q1 = Queries.getGtinbyNit(Nit)
    cursor = connection.cursor()
    cursor.execute(q1)
    Gtin14s = pd.DataFrame(data=cursor.fetchall())
    return Gtin14s
