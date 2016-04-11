from django.contrib import admin
from .models import Prioridad, Cotizacion, ProductosCotizados

# Register your models here.
admin.site.register(Prioridad)
admin.site.register(Cotizacion)
admin.site.register(ProductosCotizados)