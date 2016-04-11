from django.db import models
from apps.Pedido.models import Producto, Pedido

# Create your models here.
class Prioridad(models.Model):
	nombre = models.CharField(max_length=15)

	def __str__(self):
		return self.nombre

class Cotizacion(models.Model):
	prioridad = models.ForeignKey(Prioridad)
	pedido = models.ForeignKey(Pedido)
	cancelada = models.BooleanField()
	aprobada = models.BooleanField()
	entrega = models.IntegerField()
	fecha = models.DateField()

	def __str__(self):
		return 'Id pedido: %i - fecha: %s - prioridad: %s' % (self.pedido.id, self.fecha, self.prioridad)

class ProductosCotizados(models.Model):
	producto = models.ForeignKey(Producto)
	cotizacion = models.ForeignKey(Cotizacion)
	cantidad = models.IntegerField()
	precio = models.FloatField()
	garantia = models.IntegerField(blank=True, null=True)

	def __str__(self):
		return 'Id Cotización: %i - %s' % (self.cotizacion.id, self.producto)