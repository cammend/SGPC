from django.db import models
from apps.Deptos.models import Departamento

# Create your models here.
class Estado(models.Model):
	nombre = models.CharField(max_length=25)

	def __str__(self):
		return self.nombre

class EstadoDepto(models.Model):
	depto = models.ForeignKey(Departamento)
	estado = models.OneToOneField(Estado)

	def __str__(self):
		return '%s - %s' % (self.depto, self.estado)