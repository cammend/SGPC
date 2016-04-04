from django.db import models
from GestionUser.models import Usuario

# Create your models here.
class Departamento(models.Model):
	nombre = models.CharField(max_length=15)
	no_flujo = models.IntegerField(null=True,blank=True)

	def __str__(self):
		return self.nombre

class DeptoUser(models.Model):
	usuario = models.OneToOneField(Usuario)
	depto = models.ForeignKey(Departamento)

	def __str__(self):
		return '%s - %s' % (self.usuario, self.depto)