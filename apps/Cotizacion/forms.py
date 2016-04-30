from django import forms
from .models import Cotizacion,ProductosCotizados 
from apps.Pedido.models import Pedido, Producto



class formCotizacion(forms.ModelForm):
	class Meta:
		model = Cotizacion
		fields = ['fecha_cotizacion', 'fecha_entrega']


class formProducCotizados(forms.ModelForm):
	class Meta:
		model = ProductosCotizados
		exclude = ['prioridad', 'pedido']

class FormCotizacion(forms.ModelForm):
	def save(self, pedido, commit=True):
		cot = super(FormCotizacion, self).save(commit=False)
		cot.pedido = pedido
		cot.save()

	class Meta:
		model = Cotizacion
		fields = ['proveedor', 'fecha_cotizacion', 'fecha_entrega']


#Utilizado en apps.Depto.views
class FormProductoCotizado(forms.ModelForm):
	def save(self, cotizacion, producto, commit=True):
		prod = super(FormProductoCotizado, self).save(commit=False)
		prod.cotizacion = cotizacion
		prod.producto = producto
		prod.save()

	class Meta:
		model = ProductosCotizados
		fields = ['garantia', 'precio']