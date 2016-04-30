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

class FormAsignaRenglon(forms.ModelForm):

	def save(self, commit=True):
		ids = self.data.getlist('id')
		renglones = self.data.getlist('renglon')
		aux = 0
		for id in ids:
			Producto.objects.filter(id=id).update(renglon=renglones[aux])
			aux += 1

	class Meta:
		model = Producto
		fields = ['renglon']


#Éste es usado en apps.Depto.views
class FormRenglon(forms.ModelForm):

	class Meta:
		model = Producto
		fields = ['renglon']
