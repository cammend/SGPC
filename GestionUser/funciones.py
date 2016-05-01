from apps.Deptos.models import Departamento
from .models import Usuario, getTipos, DeptoUser

ROOT = 0
ADMIN = 1
NORMAL = 2

URL_FOR_ROOT = '/sgpc/root/'
URL_FOR_ADMIN = '/sgpc/depto/home/'


#Funciones reutilizables

#Método para obtener un 'Usuario' a partir del id
def get_user_by_id(id):
	return Usuario.objects.filter(id=id)[0]
	#Retorna un Modelo "Usuario"

#Método q regresa una lista de users filtrando por tipo (ROOT,ADMIN,NORMAL)
def get_users_by_type(tipo):
	return Usuario.objects.filter(tipoUser=tipo)
	#Retorna un Modelo "Usuario"

#Devolver todos los usuarios ADMIN
def get_admin_users():
	lista = get_users_by_type(ADMIN)
	return get_depto_user(lista)
	#Retorna un Modelo "DeptoUser"

#Devuelve todos los usuarios registrados
def get_all_user():
	return DeptoUser.objects.all().order_by('depto')

#Método para saber si se pueden agregar más usuarios ADMIN
def can_add_user_admin():
	num_reg = Usuario.objects.filter(tipoUser=ADMIN).count()
	num_dep = Departamento.objects.all().count()
	if num_reg < num_dep:
		return True
	return False
	#Retorna True o False

#Método para obtener el tipo de usuario que puede registrar otro usuario
def getTipoUser(user):
	if user.es_root(): #si el user es ROOT
		tipoU = getTipos()[1]
		t = [tipoU]
		return t
	elif user.es_admin(): #si el user es ADMIN
		tipoU = getTipos()[2]
		t = [tipoU]
		return t
	return None
	#Retorna una Lista con un elemento... el elemento es un string (ROOT,ADMIN o NORMAL)

#Método encargado de redireccionar a un usuario a la página correspondiente!
#Si existe un variables 'next' para redirección, se tomará como la de mayor prioridad
def get_url_redir(request):
	n = None
	user = request.user

	if 'next' in request.POST: n = request.POST['next']

	if user.tipoUser == ROOT:
		if n: return n
		else: return request.user.get_url_home()
	if n: return n
	else: return request.user.get_url_home()


#obtener un Depto por un id
def get_depto_by_id(id):
	return Departamento.objects.get(id=id)
	#Retorna un objeto 'Departamento'

#Método para obtener el 'Departamento' al q pertenece un usuario
def get_depto_of_user(user):
	if user.es_root():
		return None
	d_u = DeptoUser.objects.get(usuario=user)
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

def get_all_user_of_depto(user):
	return DeptoUser.objects.filter(depto=get_depto_of_user(user)).order_by('depto').values('usuario')

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