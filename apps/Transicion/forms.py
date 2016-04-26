from django import forms
from .models import Transicion, HistorialTransicion

class FormGestionar(forms.Form):
	est_act = forms.ChoiceField(label="Estado Actual")
	est_sig = forms.ChoiceField(label="Estado Siguiente")
