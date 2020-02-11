from unittest import TestCase
from administration.bussiness.prefix import Test
import json

class PrefixTestCase(TestCase):
    def test_prefix_assignment(self):
        data = u'{"AgreementName": null,"IdAgreement": null,"Request": [{"Quantity": 9,"Nit": "890900608","PreferIndicatedPrefix": false,"BusinessName": "exito","Schema": 3,"ScalePrefixes": false,"Type": 55600,"PrefixType": null,"VariedFixedUse": false}],"UserName": "sqladmin"}'

        data_json = json.loads(data)        
        resp = Test(data_json)
        self.assertEqual(resp, "", "Error al realizar la prueba")
        