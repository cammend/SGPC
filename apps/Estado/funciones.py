from GestionUser.funciones import *
from .models import Estado, EstadoDepto
from apps.Deptos.models import Departamento
from apps.Pedido.models import Pedido, Producto

#Método para saber si existe un 'Depto' asociado a un 'Estado' (EstadoDepto)
def exist_depto_in_state(user):
	depto = get_depto_of_user(user)
	return EstadoDepto.objects.filter(depto=depto).exists()

#Método para obtener una lista con todos los Deptos registrados
def get_all_deptos_registered():
	lista = Departamento.objects.all()
	l = []
	for d in lista:
		l.append(d)
	return l

#Método para obtener la lista de 'Deptos' asociados a un 'Estado' (EstadoDepto)
def get_deptos_in_estados():
	e_d = EstadoDepto.objects.filter().order_by('depto').distinct('depto')
	lista = []
	for e in e_d:
		lista.append(e.depto)
	return lista

#Método para obtener todos los pedidos que mi Depto puede Gestionar
def get_pedidos_in_my_depto(user):
	depto = get_depto_of_user(user)
	#obtener todos los estados de pedido asociados a mi Depto
	estados = EstadoDepto.objects.filter(depto=depto).values('estado')
	#con los estados asociados obtengo todos los pedidos a gestionar
	pedidos = Pedido.objects.filter(estado=estados)
	#productos = Producto.objects.select_related('pedido').filter(pedido=pedidos)
	return pedidos

#Método para obtener todos los estados posibles de un pedido
def get_all_estados():
	qEst = Estado.objects.all()
	estados = []
	for est in qEst:
		estados.append(est)
	return estados

#Método para obtener todos los estados asociados a un depto
def get_estados_in_depto(depto):
	qEstDep = EstadoDepto.objects.filter(depto=depto).order_by('estado')
	estados = []
	for q in qEstDep:
		estados.append(q.estado)
	return estados

#Método para obtener todos los estados no asociados a un depto
def get_estados_out_depto(depto):
	estados_in = get_estados_in_depto(depto)
	estados = get_all_estados()
	for est_in in estados_in:
		aux = 0
		for est in estados:
			if est.id == est_in.id:
				del estados[aux]
				continue
			else: aux += 1
	return estados