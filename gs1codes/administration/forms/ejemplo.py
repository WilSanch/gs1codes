from django import forms
from material.base import Layout
from django.template import RequestContext
from django.shortcuts import render_to_response


class EjemploForm(forms.Form):
    nit = forms.CharField()
    empresa= forms.CharField()
    layout = Layout('nit','empresa')

