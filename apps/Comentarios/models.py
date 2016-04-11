from django.db import models
from GestionUser.models import Usuario
from apps.Cotizacion.models import Cotizacion
from apps.Pedido.models import Pedido

# Create your models here.
class Comentario(models.Model):
	usuario = ForeingKey(Usuario)
	cotizacion = ForeingKey(Cotizacion)
	titulo = models.CharField(max_length=25)
	descripcion = models.TextField()
	fecha = models.DateField()

	def __str__(self):
		return self.titulo

class Observacion(models.Model):
	usuario = ForeingKey(Usuario)
	pedido = ForeingKey(Pedido)
	titulo = models.CharField(max_length=25)
	descripcion = models.TextField()
	fecha = models.DateField()

	def __str__(self):
		return self.titulo