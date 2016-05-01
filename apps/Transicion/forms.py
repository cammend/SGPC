from django import forms
from .models import Transicion, HistorialTransicion
from apps.Estado.models import Estado

def choice_actual(pedido):
	t = Transicion.objects.filter(estadoActual = pedido.estado).values('estadoActual')
	return Estado.objects.filter(id = t)

def choice_siguiente(pedido):
	t = Transicion.objects.filter(estadoActual = pedido.estado)
	return Estado.objects.filter(siguiente = t)

class FormGestionar(forms.Form):
	est_act = forms.ModelChoiceField(label="Estado Actual", queryset=Transicion.objects.all(), empty_label=None)
	est_sig = forms.ModelChoiceField(label="Estado Siguiente", queryset=Transicion.objects.all(), empty_label='Elija opción')
