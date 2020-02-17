from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _
from simple_history.models import HistoricalRecords

class State(models.Model):
    """ 
    Representa los estados del GTIN 
    """
    
    description = models.CharField(max_length=50)
    """
    Descripcion del estado del GTIN 
    """
    
    active = models.BooleanField()
    """
    Estado del registro
    """
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("States")
    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("State_detail", kwargs={"pk": self.pk})
   
class Range(models.Model):
    """
    Representa los rangos que pueden tener un prefijo
    """
    country_code= models.CharField(max_length=5,blank=True, null=True)
    """
    Representa el prefijo del pais
    """
    name = models.CharField(max_length=50)
    """
    Nombres del rango
    """
    
    description = models.CharField(max_length=50)
    """
    Descripcion del rango
    """
    
    quantity_code = models.BigIntegerField()
    """
    Cantidad de codigos que se peuden generar en el rango
    """
    
    initial_value = models.BigIntegerField()
    """
    Valor inicial del rango
    """

    final_value = models.BigIntegerField()
    """
    Valor final del rango
    """
    
    regrouping =  models.BooleanField()
    """
    representa si se permite reagrupacion del rango
    """
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Range")
        verbose_name_plural = _("Ranges")
        
    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("Range_detail", kwargs={"pk": self.pk})

class ProductType(models.Model):
    """
    Representa los tipos de producto que puede tener un GTIN
    """
    
    description = models.CharField(max_length=100)
    """
    Descripcion del tipo de producto
    """
    
    state =  models.BooleanField()
    """
    Estado del tipo de producto
    """
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("ProductType")
        verbose_name_plural = _("ProductTypes")

    # def __str__(self):
    #     return str(self.id)

    def get_absolute_url(self):
        return reverse("ProductType_detail", kwargs={"pk": self.pk})

class AtcCategory(models.Model):
    """
    Representa las categorias ATC para los farmaceuticos
    """
    
    code = models.CharField(max_length=20)
    """
    Codigo de la categoria ATC
    """
    
    name= models.CharField(max_length=200)
    """
    Nombre de la categoria ATC
    """
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("atc_category")
        verbose_name_plural = _("atc_categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("atc_category_detail", kwargs={"pk": self.pk})
    
class TextilCategory(models.Model):
    """
    Representa las categorias para los productos Textiles
    """
    
    code = models.CharField(max_length=20)
    """
    Codigo de la categoria Textil
    """
    
    name= models.CharField(max_length=200)
    """
    Nombre de la categoria Textil
    """
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("textil_category")
        verbose_name_plural = _("textil_categories")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("textil_category_detail", kwargs={"pk": self.pk})

class Country(models.Model):
    """
    Representa los codigos de los paises
    """
    
    iso_n3 = models.CharField(primary_key=True, max_length=3)
    """
    nomenclatura iso_3
    """
    
    iso_a2 =  models.CharField(max_length=2)
    """
    nomenclatura a_2
    """
    
    iso_a3 = models.CharField(max_length=3)    
    """
    nomenclatura a_3
    """
    
    name = models.CharField(max_length=100)    
    """
    nombre del pais
    """
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("target_market")
        verbose_name_plural = _("target_markets")
        
    def __str__(self):
        return self.iso_a3

    def get_absolute_url(self):
        return reverse("target_market_detail", kwargs={"pk": self.pk})

class ProductState(models.Model):
    """
    Representa los estados que puede tener un Gtin como producto 
    """
    
    description = models.CharField(max_length=50)
    """
    Descripcion del estado
    """   
    
    active = models.BooleanField()
    """
    Estado del registro
    """   
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("product_state")
        verbose_name_plural = _("product_states")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("product_state_detail", kwargs={"pk": self.pk})

class MeasureUnit(models.Model):
    """
    Representacion de las unidades de medidas de un producto
    """   
    
    code = models.CharField(max_length=5)           
    """
    Codigo de la unidad de medida
    """   
    
    description = models.CharField(max_length=50)
    """
    Descripcion de la unidad de medida
    """   
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("measure_unit")
        verbose_name_plural = _("measure_units")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("measure_unit_detail", kwargs={"pk": self.pk})
    
class GpcCategory(models.Model):
    """
    Representacion de las categorias GPC
    """   
    
    segment_code = models.CharField(max_length=200)
    """
    Codigo del segmento
    """   
    
    segment_description = models.CharField(max_length=200)
    """
    Descripcion del segmento Ingles
    """   
    
    family_code = models.CharField(max_length=200)           
    """
    Codigo de la familia Ingles
    """   
    
    family_description = models.CharField(max_length=200)
    """
    Descripcion de la familia Ingles
    """   
    
    class_code = models.CharField(max_length=200)
    """
    Codigo de la clase Ingles
    """   
    
    class_description = models.CharField(max_length=200)
    """
    Descripcion de la clase Ingles
    """   
    
    brick_code = models.CharField(max_length=200)
    """
    Codigo del brick Ingles
    """   
    
    brick_description = models.CharField(max_length=200)
    """
    Descripcion del brick Ingles
    """   
    
    spanish_name_segment = models.CharField(max_length=200)
    """
    Descripcion del segmento Español
    """ 
    
    spanish_name_family = models.CharField(max_length=200)
    """
    Descripcion de la familia Ingles
    """ 
    
    spanish_name_class = models.CharField(max_length=200)
    """
    Descripcion de la clase Español
    """ 
    
    spanish_name_brick = models.CharField(max_length=200)
    """
    Descripcion del brick Español
    """
    
    history = HistoricalRecords()    

    class Meta:
        verbose_name = _("gpc_category")
        verbose_name_plural = _("gpc_categorys")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("gpc_category_detail", kwargs={"pk": self.pk})

class Schema(models.Model):
    """
    Representa los esquemas de los prefijos
    """
    
    description = models.CharField(max_length=50)
    """
    Descripcion del esquemas
    """
    
    validity_time = models.IntegerField()
    """
    Años de validez del esquema
    """
    
    state = models.BooleanField()
    """
    Estado del esquema
    """
    
    validity_date = models.DateField(auto_now=False, auto_now_add=False, null=True)
    """
    Fecha de validacion del esquema
    """
    
    validate_from_creation_date = models.BooleanField()
    """
    Descripcion des esquemas
    """
    
    class Meta:
        verbose_name = _("schema")
        verbose_name_plural = _("schemas")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("schema_detail", kwargs={"pk": self.pk})

class Enterprise(models.Model):
    """
    Representa la empresas
    """
    
    identification =  models.CharField(max_length=20)
    """
    Documento de indentificacion
    """
    
    country =  models.ForeignKey(Country, verbose_name=_("country_enteprise"), on_delete=models.CASCADE)
    """
    Pais de la empresa
    """
    
    code_quantity_purchased =  models.IntegerField(blank=True, null=True)
    """
    Cantidad de codigos comprados
    """
    
    code_quantity_consumed =  models.IntegerField(blank=True, null=True)
    """
    Cantidad de codigos consumidos
    """
    
    code_quantity_reserved =  models.IntegerField(blank=True, null=True)
    """
    Cantidad de codigos reservados
    """
    
    code_residue =  models.IntegerField(blank=True, null=True)
    """
    Cantidad de codigos del saldo
    """
    
    return_codes =  models.BooleanField(blank=True, null=True)
    """
    Cantidad de codigos comprados
    """
    
    return_process =  models.BooleanField(blank=True, null=True)
    """
    Realiza proceso de devolucion
    """
    
    enterprise_name =  models.CharField(max_length=200)
    """
    Nombre de la empresa
    """
    
    enterprise_state =  models.BooleanField()
    """
    Estado de la empresa
    """
    
    date_return_codes = models.DateTimeField(auto_now=False, auto_now_add=False, blank=True, null=True)
    """
    Fecha de retorno de codigos
    """
    
    history = HistoricalRecords()    

    class Meta:
        verbose_name = _("enterprise")
        verbose_name_plural = _("enterprises")
        unique_together = [['country', 'identification']]

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("enterprise_detail", kwargs={"pk": self.pk})

class Prefix(models.Model):
    """
    Representa los prefijos
    """
    
    id = models.BigAutoField(primary_key=True)
    """
    Id del prefijo
    """
    
    id_prefix = models.BigIntegerField()
    """
    Id prefijo
    """
    
    state =  models.ForeignKey(State, verbose_name=_("State_Prefix"), on_delete=models.CASCADE)  
    """
    Estado del prefijo
    """
    
    enterprise = models.ForeignKey(Enterprise, verbose_name=_("enterprise_prefix"), on_delete=models.CASCADE, blank=True, null=True)
    """
    Empresa a ala cual pertenece el prefijo
    """
    
    range = models.ForeignKey(Range, verbose_name=_("range_prefix"), on_delete=models.CASCADE)
    """
    Rango del prefijo
    """
    
    schema = models.ForeignKey(Schema, verbose_name=_("schema_prefix"), on_delete=models.CASCADE,blank=True, null=True)
    """
    Esquema del prefijo
    """
    
    assignment_date = models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
    """
    Fecha de asignacion
    """
    
    validity_date =models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
    """
    Fecha de validacion
    """
    
    inactivation_date =models.DateTimeField(auto_now=False, auto_now_add=False,blank=True, null=True)
    """
    Fecha de inactivacion
    """
    
    observation =  models.CharField(max_length=500)
    """
    Observacion
    """
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Prefix")
        verbose_name_plural = _("Prefixes")
        unique_together = [['range', 'id_prefix']]
    def __str__(self):
        return f'{self.range} ➔ {self.id_prefix}' 

    def get_absolute_url(self):
        return reverse("Prefix_detail", kwargs={"pk": self.pk})

class AgreementType(models.Model):
    """
    Representa el tipo de convenio
    """
    
    name= models.CharField(max_length=50)
    """
    nombre del convenio
    """
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("AgreementType")
        verbose_name_plural = _("AgreementTypes")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("AgreementType_detail", kwargs={"pk": self.pk})

class Agreement(models.Model):
    """
    Representa el Contrato
    """
    
    name = models.CharField(max_length=200)
    """
    Nombre del contrato
    """
    
    type = models.ForeignKey(AgreementType, verbose_name=_(""), on_delete=models.CASCADE)
    """
    Tipo del contrato
    """
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Agreament")
        verbose_name_plural = _("Agreaments")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Agreament_detail", kwargs={"pk": self.pk})
    
class Brand(models.Model):
    """
    Representa las marcas de un producto
    """
    
    name = models.CharField(max_length=200)
    """
    Nombre de la marca
    """

    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Brand_detail", kwargs={"pk": self.pk})

class Code(models.Model):
    """
    Representa los codigos GTIN
    """
    
    id = models.BigAutoField(primary_key=True)
    """
    Gtin o Codigo
    """
    
    alternate_code = models.CharField(max_length=100, blank=True, null=True)
    """
    Para almacenar el codigo internacional
    """
    
    prefix = models.ForeignKey(Prefix, on_delete=models.CASCADE)
    """
    prefijo asociado al codigo
    """
    
    description = models.CharField(max_length=200, blank=True, null=True)
    """
    descripcion de codigo
    """
    
    assignment_date = models.DateTimeField(blank=True, null=True)
    """
    Fecha de asignacion
    """
    
    product_type = models.ForeignKey(ProductType , on_delete=models.CASCADE, related_name="ProductType_Code",blank=True, null=True)
    """
    tipo de producto del codigo
    """
    
    range = models.ForeignKey(Range , on_delete=models.CASCADE, related_name="Range_Code", null=True)
    """
    rango del codigo
    """
    
    state = models.ForeignKey(State , on_delete=models.CASCADE, related_name="State_Code")
    """
    estado del codigo
    """
    
    agreement =  models.ForeignKey(Agreement, verbose_name=_("agreement_id"), on_delete=models.CASCADE, null= True)
    """
    tipo de contrato o convenio
    """
    
    brand =  models.ForeignKey(Brand, verbose_name=_("brand_code"), on_delete=models.CASCADE, null=True)
    """
    marca del producto
    """
    
    gpc_category = models.ForeignKey(GpcCategory, on_delete=models.CASCADE, null=True)
    """
    Categoria GPC
    """
    
    atc_category = models.ForeignKey(AtcCategory, on_delete=models.CASCADE, null=True, related_name="codes")
    """
    Categoria ATC farmaceutico
    """
    
    textil_category = models.ForeignKey(TextilCategory, on_delete=models.CASCADE, blank=True, null=True, related_name="codes")
    """
    Categoria Textil
    """
    
    target_market = models.ForeignKey(Country, on_delete=models.CASCADE, blank=True, null=True)
    """
    Marcado obejtivo
    """
    
    url = models.CharField(max_length=500, blank=True, null=True)
    """
    Url de la imagen
    """
    
    product_state = models.ForeignKey(ProductState, on_delete=models.CASCADE, blank=True, null=True)
    """
    estado del producto
    """
    
    measure_unit =  models.ForeignKey(MeasureUnit, on_delete=models.CASCADE, blank=True, null=True, related_name="codes")
    """
    unidad de medida
    """
    
    quantity_code = models.DecimalField(max_digits=5, decimal_places=2,blank=True, null=True)
    """
    cantidad contenida
    """
    
    gln_name = models.CharField(max_length=100,blank=True, null=True)
    """
    nombre de la ubicacion
    """
    
    history = HistoricalRecords()
    
    class Meta:
        verbose_name = _("Code")
        verbose_name_plural = _("Codes")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("Code_detail", kwargs={"pk": self.pk})
    
class Code_Gtin14(models.Model):
    """
    Representa la unidades de empaque Gtin14
    """
    
    id = models.BigIntegerField(primary_key=True)
    """
    Codigo Gtin14
    """
    
    id_code =  models.ForeignKey(Code, verbose_name=_("Code_code_gtin14"), on_delete=models.CASCADE)
    """
    Gtin13 asociado
    """
    
    description =  models.CharField(max_length=500)
    """
    descripcion de la unidad de empaque
    """
    
    state =  models.ForeignKey(State, verbose_name=_("state_code_gtin14"), on_delete=models.CASCADE, blank=True, null=True)
    """
    stado de la unidade de empaque
    """
    
    quantity = models.DecimalField(max_digits=5, decimal_places=2)
    """
    cantidad contenida de la unidad de empaque
    """
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = _("Code_Gtin14")
        verbose_name_plural = _("Code_Gtin14s")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("Code_Gtin14_detail", kwargs={"pk": self.pk})




class CodeTypeByRanges(models.Model):
    """
    Representa el código del tipo
    """
    code_type = models.IntegerField()
    """
    Representa el código del rango
    """
    range = models.ForeignKey(Range, verbose_name=_("Range_CodeTypeByRanges"), on_delete=models.CASCADE,blank=True, null=True)

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("CodeTypeByRange")
        verbose_name_plural = _("CodeTypeByRanges")
        
    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("CodeTypeByRanges_detail", kwargs={"pk": self.pk})


class CodeTypeBySchemas(models.Model):
    """
    Representa el código del tipo
    """
    code_type = models.IntegerField()
    """
    Representa el código del esquema
    """
    schema = models.ForeignKey(Schema, verbose_name=_("schema_CodeTypeBySchemas"), on_delete=models.CASCADE,blank=True, null=True)
    """
    Representa si se le da el prefijo
    """    
    give_prefix = models.IntegerField()

    history = HistoricalRecords()

    class Meta:
        verbose_name = _("CodeTypeBySchemas")
        verbose_name_plural = _("CodeTypeBySchemas")
        
    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse("CodeTypeBySchemas_detail", kwargs={"pk": self.pk})

