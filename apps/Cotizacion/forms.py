from django import forms
from .models import Cotizacion,ProductosCotizados 



class formCotizacion(forms.ModelForm):
	class Meta:
		model = Cotizacion
		fields = ['fecha', 'entrega']


class formProducCotizados(forms.ModelForm):
	class Meta:
		model = ProductosCotizados
		exclude = ['prioridad', 'pedido']