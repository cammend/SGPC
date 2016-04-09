from django.db import models
from apps.Estado.models import Estado

#Create your models here.
class Transicion(models.Model):
	descripcion = models.CharField(max_length=30)
	estadoActual = models.ForeignKey(Estado, related_name='actual')
	estadoSiguiente = models.ForeignKey(Estado, related_name='siguiente')

	def __str__(self):
		return self.descripcion

class HistorialTransicion(models.Model):
	transicion = models.ForeignKey(Transicion)