from apps.Pedido.models import Pedido, Producto
from GestionUser.funciones import *
from .models import Departamento, DeptoUser

ROOT = 0
ADMIN = 1
NORMAL = 2

#obtener un Depto por un id
def get_depto_by_id(id):
	return Departamento.objects.get(id=id)
	#Retorna un objeto 'Departamento'

#Método para obtener el 'Departamento' al q pertenece un usuario
def get_depto_of_user(user):
	d_u = DeptoUser.objects.filter(usuario=user)[0]
	return d_u.depto
	#Retorna un objeto 'Departamento'

#Método para obtener la relación 'Usuario - Departamento' para una lista de usuarios o usuario individual
def get_depto_user(list_user):
	return DeptoUser.objects.filter(usuario=list_user).order_by('depto')
	#Retorna un Modelo "DeptoUser"

#Método para obtener la relación 'Usuario - Departamento' para una lista de deptos o depto individual
def get_user_depto(list_depto):
	return DeptoUser.objects.filter(depto=list_depto).order_by('depto')
	#Retorna un Modelo "DeptoUser"

#Devuelve todos los usuarios pertenecientes a un Departamento
def get_all_user_by_depto(user):
	return DeptoUser.objects.filter(depto=get_depto_of_user(user)).order_by('depto')
	#Retorna un Modelo "DeptoUser"

#Devuelve todos los usuarios NORMALES pertenecientes al Depto de éste Usuario ADMIN
def get_normal_user_by_depto(user):
	lista = get_users_by_type(NORMAL)
	return DeptoUser.objects.filter(usuario=lista, depto=get_depto_of_user(user)).order_by('depto')
	#Retorna un Modelo "DeptoUser"

#Método para obtener los deptos que no tengan un user ADMIN asignado, si el usuario logueado es ROOT
#O si el usuario logueado es un ADMIN, pues se obtiene el Depto al q pertenece
def getListaDeptos(user):
	lista = []
	lista.append(('','-----')) #ésta es la opción por default
	if user.es_root() and can_add_user_admin():
		tipos = Usuario.objects.filter(tipoUser=ADMIN) #obtengo todos los usuarios ADMIN
		depto_user = DeptoUser.objects.filter(usuario=tipos).order_by('depto') #se obtienen todos los usuarios ADMIN asignados a un depto
		deptos = Departamento.objects.exclude(deptouser=depto_user) #se excluyen todos deptos q ya tengan un user ADMIN asignado
		#Hasta aquí ya se tienen la lista de deptos q no tienen un user ADMIN asignado
		for d in deptos:
			lista.append( (d.id,d.nombre) ) #se añaden tuplas a la lista
	elif user.es_admin():
		d_u = DeptoUser.objects.filter(usuario=user)[0] #Buscamos la relación "Usuario-Depto"
		d = d_u.depto #Escogemos solo el Depto
		lista = [] #Vaciamos la lista
		lista.append( (d.id,d) ) #Almacenamos la tupla dentro de la lista
	return lista
	#Devuelve una Lista