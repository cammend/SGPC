from django.contrib import admin
from .models import Pedido, Producto

# Register your models here.
admin.site.register(Pedido)
admin.site.register(Producto)