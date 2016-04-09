from django.contrib import admin
from .models import Transicion, HistorialTransicion

# Register your models here.
admin.site.register(Transicion)
admin.site.register(HistorialTransicion)