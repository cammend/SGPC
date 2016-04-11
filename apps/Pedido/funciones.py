from GestionUser.model import Usuario
from .models import Pedido, Producto
from GestionUser.funciones import *

NO_PUBLICADO = 1
COTIZACION_ORD = 6
RETIRADO_ALMACEN = 10

#Método para obtener todos los pedidos hechos por el usuario actual
def get_all_pedidos(user):
	return Pedido.objects.filter(usuario=user)

#Método para obtener todos los productos de un pedido
def get_all_producto_of_pedido(pedido):
	return Producto.objects.filter(pedido=pedido)



