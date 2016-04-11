from apps.Deptos.models import Departamento, DeptoUser
from .models import Usuario, getTipos

#Funciones reutilizables

ROOT = 0
ADMIN = 1
NORMAL = 2

#Método para obtener un 'Usuario' a partir del id
def get_user_by_id(id):
	return Usuario.objects.filter(id=id)[0]
	#Retorna un Modelo "Usuario"

#Método para obtener el 'Departamento' al q pertenece un usuario
def get_depto_of_user(user):
	query = DeptoUser.objects.filter(usuario=user)[0]
	return query.depto
	#Retorna un Modelo "Departamento"

#Método q regresa una lista de users filtrando por tipo (ROOT,ADMIN,NORMAL)
def get_users_by_type(tipo):
	return Usuario.objects.filter(tipoUser=tipo)
	#Retorna un Modelo "Usuario"

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

#Método para obtener el tipo de usuario que puede registrar otro usuario
def getTipoUser(user):
	if user.tipoUser == ROOT: #si el user es ROOT
		tipoU = getTipos()[1]
		t = [tipoU]
		return t
	elif user.tipoUser == ADMIN: #si el user es ADMIN
		tipoU = getTipos()[2]
		t = [tipoU]
		return t
	return None

#Método para obtener los deptos que no tengan un user ADMIN asignado; o solo el depto del user ADMIN
def getListaDeptos(user):
	lista = []
	lista.append(('','-----')) #ésta es la opción por default
	if user.tipoUser == ROOT and can_add_user_admin():
		tipos = Usuario.objects.filter(tipoUser=ADMIN) #obtengo todos los usuarios ADMIN
		depto_user = DeptoUser.objects.filter(usuario=tipos).order_by('depto') #se obtienen todos los usuarios ADMIN asignados a un depto
		deptos = Departamento.objects.exclude(deptouser=depto_user) #se excluyen todos deptos q ya tengan un user ADMIN asignado
		#Hasta aquí ya se tienen la lista de deptos q no tienen un user ADMIN asignado
		for d in deptos:
			lista.append((d.id,d.nombre)) #se añaden tuplas a la lista
		return lista
	elif user.tipoUser == ADMIN:
		d_u = DeptoUser.objects.filter(usuario=user)[0]
		d = d_u.depto
		depto = [(d.id,d)]
		return depto
	return None

#Método para asignar campos 'choices' a un form
def agregarChoices(form, request):
	form.fields['tipo'].choices = getTipoUser(request.user)
	form.fields['departamento'].choices = getListaDeptos(request.user)
	return form