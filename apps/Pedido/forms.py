from django import forms
from .models import Pedido, Producto
from apps.Estado.models import Estado



class FormPedido(forms.ModelForm):
	class Meta:
		model = Pedido
		fields = ['justificacion', 'fecha']

	def save(self, user, commit=True):
		# Save the provided password in hashed format
		pedido = super(FormPedido, self).save(commit=False)
		pedido.usuario = user
		pedido.estado = Estado.objects.get(id=1)
		if commit:
			pedido.save()
		return pedido


class FormProducto(forms.ModelForm):
	class Meta:
		model = Producto
		fields = ['descripcion', 'cantidad', 'precio']

	def save(self, pedido, commit=True):
		# Save the provided password in hashed format
		producto = super(FormProducto, self).save(commit=False)
		producto.pedido = pedido
		if commit:
			producto.save()
		return producto