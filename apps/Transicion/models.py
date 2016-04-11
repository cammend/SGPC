from django.db import models
from apps.Estado.models import Estado
from apps.Pedido.models import Pedido
from GestionUser.models import Usuario

#Create your models here.
class Transicion(models.Model):
	descripcion = models.CharField(max_length=30)
	estadoActual = models.ForeignKey(Estado, related_name='actual')
	estadoSiguiente = models.ForeignKey(Estado, related_name='siguiente')

	def __str__(self):
		return '%s --> %s' % (self.estadoActua, self.estadoSiguiente)

	def get_descripcion(self):
		return self.descripcion

class HistorialTransicion(models.Model):
	pedido = models.ForeignKey(Pedido)
	transicion = models.ForeignKey(Transicion)
	usuario = models.ForeignKey(Usuario)
	fecha = models.DateField()

	def __str__(self):
		return 'Id Pedido: %s - Fecha: %s - Transición: %s' % (self.pedido.id, self.fecha, self.transicion)