from django import forms
from .models import Departamento


class ListaDeptos(forms.Form):
	departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())