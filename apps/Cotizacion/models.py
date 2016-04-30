from django.db import models
from apps.Pedido.models import Producto, Pedido

# Create your models here.
class Prioridad(models.Model):
	nombre = models.CharField(max_length=15)

	def __str__(self):
		return self.nombre

class Cotizacion(models.Model):
	prioridad = models.ForeignKey(Prioridad, null=True)
	pedido = models.ForeignKey(Pedido)
	cancelada = models.BooleanField(default=False)
	aprobada = models.BooleanField(default=False)
	proveedor = models.CharField(max_length=50)
	fecha_cotizacion = models.DateField(verbose_name='Fecha de ésta Cotización')
	fecha_entrega = models.DateField(verbose_name='Fecha de Entrega del Pedido')

	def __str__(self):
		return 'Id pedido: %i - fecha: %s - prioridad: %s' % (self.pedido.id, str(self.fecha_cotizacion), self.prioridad)

class ProductosCotizados(models.Model):
	producto = models.ForeignKey(Producto)
	cotizacion = models.ForeignKey(Cotizacion, verbose_name='Cotización')
	garantia = models.IntegerField(blank=True, null=True, verbose_name='Garantía (meses)')
	cantidad = models.IntegerField(null=True)
	precio = models.FloatField(null=True)

	def __str__(self):
		return 'Id Cotización: %i - %s' % (self.cotizacion.id, self.producto)

	def total(self):
		if not self.cantidad or not self.precio:
			return 0
		return self.cantidad * self.precio