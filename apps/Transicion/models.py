from django.db import models
from apps.Estado.models import Estado
from apps.Pedido.models import Pedido
from GestionUser.models import Usuario

#Create your models here.
class Transicion(models.Model):
	descripcion = models.CharField(max_length=50)
	estadoActual = models.ForeignKey(Estado, related_name='actual', verbose_name='Estado actual')
	estadoSiguiente = models.ForeignKey(Estado, related_name='siguiente', verbose_name='Estado siguiente')

	def __str__(self):
		return '%s - (%s --> %s)' % (self.descripcion, self.estadoActual, self.estadoSiguiente)

	def get_descripcion(self):
		return self.descripcion

class HistorialTransicion(models.Model):
	pedido = models.ForeignKey(Pedido)
	transicion = models.ForeignKey(Transicion,verbose_name='Transición')
	usuario = models.ForeignKey(Usuario)
	fecha = models.DateField()

	def __str__(self):
		return 'Id Pedido: %s - Fecha: %s - Transición: %s' % (self.pedido.id, str(self.fecha), self.transicion)