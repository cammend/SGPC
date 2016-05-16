from django import forms
from .models import Comentario, Observacion

class FormComentarioPedido(forms.ModelForm):

	def save(self, usuario, pedido):
		com = super(FormComentarioPedido, self).save(commit=False)
		com.usuario = usuario
		com.pedido = pedido
		com.save()

	class Meta:
		model = Observacion
		fields = ['titulo','descripcion']

class FormComentarioCot(forms.ModelForm):

	def save(self, usuario, cotizacion):
		com = super(FormComentarioCot, self).save(commit=False)
		com.usuario = usuario
		com.cotizacion = cotizacion
		com.save()
		
	class Meta:
		model = Comentario
		fields = ['titulo','descripcion']