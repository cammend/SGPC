from .models import Pedido, Producto
from apps.Deptos.funciones import *
from GestionUser.funciones import *

NO_PUBLICADO = 1
COTIZACION_ORD = 6
RETIRADO_ALMACEN = 10

#Método para obtener todos los pedidos hechos por un usuario
def get_all_pedidos_by_user(user):
	return Pedido.objects.filter(usuario=user)

#Método para obtener todos los productos de un pedido
def get_all_producto_of_pedido(pedido):
	return Producto.objects.filter(pedido=pedido)

#Método para obtener todos los pedidos pertenecientes a un Depto
def get_all_pedidos_by_depto(user):
	lista_u = get_all_user_by_depto(user)
	lista_p = []
	for u in lista_u:
		lista = Pedido.objects.filter(usuario=u.usuario)
		for p in lista:
			lista_p.append(p)
	return lista_p
	#Retorna una Lista

#Método que retorna todos los pedidos gestionados en el Depto del usuario logueado
def get_all_gestion_by_depto(user):
	q_lista_users = get_all_user_by_depto(user)
	q_lista_pedido = Pedido.objects.filter(usuario=q_lista_users)
	for p in q_lista_pedido:
		q_lista_pedido.appendlist( 'trans',get_all_historial_pedido(p) )
	return q_lista_pedido

def get_all_productos_by_depto(user):
	lista_p = get_all_pedidos_by_depto(user)
	for p in lista_p:
		pass	

def get_depto_of_pedido(pedido):
	user = pedido.usuario
	return get_depto_of_user(user)

#Método para generar una lista de ids de alguna lista de Modelos
def generate_list_of_id(list_model):
	lista_ids = []
	for l in list_model:
		lista_ids.append(l.id)
	return lista_ids

#Pasando un id de un modelo, me devuelve el id de la list_model
def get_index_of_list_model(id, list_model):
	aux = 0
	for l in list_model:
		if (l.id == id): return aux
		else: aux += 1
	return None

def get_next_of_list_model(id, list_model):
	enviar = False
	for l in list_model:
		if enviar: return l
		if (int(l) == int(id)): enviar = True
	return None

def get_back_of_list_model(id, list_model):
	aux = None
	primero = True
	for l in list_model:
		if (int(l) == int(id)): return aux
		if primero:	primero = False
		else: aux = l
	return None