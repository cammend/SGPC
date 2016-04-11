from django.db import models
from GestionUser.models import Usuario
from apps.Estado.models import Estado

# Create your models here.
class Pedido(models.Model):
	usuario = models.ForeignKey(Usuario)
	estado = models.OneToOneField(Estado)
	justificacion = models.TextField()
	fecha = models.DateField(auto_now_add=True)
	total = models.FloatField(blank=True, null=True)

	def __str__(self):
		return 'Usuario: %s - Fecha: %s - Estado: %s' % (self.usuario, str(self.fecha), self.estado)

class Producto(models.Model):
	pedido = models.ForeignKey(Pedido)
	descripcion = models.TextField()
	cantidad = models.IntegerField()
	precio = models.FloatField()
	renglon = models.IntegerField(blank=True,null=True)

	def __str__(self):
		return 'Id Pedido: %i - Descripción: %s' % (self.pedido.id, self.descripcion)