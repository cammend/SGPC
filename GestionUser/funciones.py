from apps.Deptos.models import Departamento, DeptoUser
from .models import Usuario, getTipos

ROOT = 0
ADMIN = 1
NORMAL = 2

URL_FOR_ROOT = '/sgpc/cuentas/'
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
		else: return URL_FOR_ROOT
	if n: return n
	else: return URL_FOR_ADMIN