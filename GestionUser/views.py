from django.shortcuts import render, redirect
from .forms import UsuarioForm
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import getDeptos, getTipos
from apps.Deptos.models import Departamento, DeptoUser
from .funciones import *
from apps.Deptos.funciones import *

ROOT = 0
ADMIN = 1
NORMAL = 2

URL_FOR_ROOT = '/sgpc/cuentas/'
URL_FOR_ADMIN = '/sgpc/depto/home/'

#Método para asignar campos 'choices' a un form
def agregarChoices(form, request):
	form.fields['tipo'].choices = getTipoUser(request.user)
	form.fields['departamento'].choices = getListaDeptos(request.user)
	return form


# VISTAS

#Vista para eliminar un usuario re-confirmado
@login_required
def eliminarSeguridad(request):
	user = request.user
	ctx = {}
	ctx['titulo'] = 'Error'
	ctx['titulo_msg'] = 'Operación no permitida!'
	ctx['msg'] = '''El usuario a eliminar no puede ser borrado!\n
	Compruebe que tiene permisos para borrar cuentas de usuario.'''
	ctx['url_redir'] = '/sgpc/cuentas/eliminar/'

	if request.method == 'POST' and 'usuario' in request.POST:
		id = request.POST['usuario']
		d_u = get_depto_user(get_user_by_id(id))[0]
		ctx['usuario'] = d_u.usuario
		ctx['depto'] = d_u.depto
	elif request.method == 'POST':
		id = request.POST['id'] #obtenemos el id por vía 'POST'
		list_u = Usuario.objects.filter(id=id) #Obtenemos un queryset de el usuario
		u = list_u[0] #Sacamos al usuario del queryset
		if user.es_root(): #Comprobamos q el user de la sesión sea ROOT
			if u.es_admin(): #Comprobamos q el usuario a eliminar sea ADMIN
				print('Eliminado user admin')
				#list_u.delete() #Si es ADMIN, lo eliminamos
			else:
				return render(request, 'GestionUser/info.html', ctx)
		elif user.es_admin(): #Si el user de la sesión es admin
			id_1 = get_depto_of_user(user).id #Obtenemos el id depto de éste user
			id_2 = get_depto_of_user(u).id #obtenemos el id depto del user a eliminar
			#Comprobamos que el depto de usuario registrado y el del usuario a eliminar sean iguales
			#Luego verificamos que el usuario a eliminar sea NORMAL
			if (id_1 == id_2) and u.es_normal():
				print('Eliminado user normal')
				#list_u.delete()
			else:
				return render(request, 'GestionUser/info.html', ctx)

		ctx['titulo'] = 'Eliminado!'
		ctx['titulo_msg'] = 'Usuario Eliminado!'
		ctx['msg'] = 'Usuario eliminado exitosamente.'
		return render(request, 'GestionUser/info.html', ctx)
	else:
		return redirect('/sgpc/cuentas/eliminar/')
	return render(request, 'GestionUser/eliminar_seguro.html', ctx)

#Vista que no elimina, pero reenvía a una vista para confirmar la eliminación!
@login_required
def eliminarUsuario(request):
	user = request.user
	users = []
	ctx = {}
	if user.es_root(): #si el usuario es ROOT
		#Obtener todos los usuarios ADMIN
		users = get_admin_users() #devuelve todos los ADMIN
		ctx['is_root'] = True
	elif user.es_admin(): #si el usuario es ADMIN
		#Obtener todos los usuarios NORMALES pero pertenencientes al Depto de éste user ADMIN
		users = get_normal_user_by_depto(request.user)
	else:
		return redirect('/sgpc/depto/home/')
	ctx['lista'] = users
	ctx['h1'] = 'Eliminar Usuarios'
	return render(request, 'GestionUser/eliminar_usuario.html', ctx)

@login_required
def crearUsuario(request):
	form = UsuarioForm()
	form = agregarChoices(form, request)
	ctx = {'form': form}
	ctx['h1'] = 'Nuevo Usuario'
	if not can_add_user_admin(): #si no se pueden agregar más usuarios ADMIN
		ctx['p'] = 'No se pueden agregar más usuarios!'
	if request.method == 'POST':
		form = UsuarioForm(request.POST)
		form = agregarChoices(form, request)
		print(request.POST)
		if form.is_valid():
			form.save()
			ctx = {'titulo': 'Guardado',
				   'titulo_msg': 'Usuario Guardado!',
				   'msg': 'Usuario guardado correctamente!',
				   'url_redir': '/sgpc/cuentas/nueva/'}
			return render(request, 'GestionUser/info.html', ctx)
		else:
			ctx['form'] = form
			
	return render(request, 'GestionUser/crear_usuario.html', ctx)

@login_required
def index(request):
	user = request.user
	ctx = {}
	if user.es_normal():
		return redirect('/sgpc/depto/home/')
	elif user.es_admin():
		#Obtener todos los usuarios Normales registrado por éste usuario ADMIN
		d_u = get_all_user_by_depto(request.user)
		depto = get_depto_of_user(request.user)
		ctx = {'lista':d_u,
			   'h1':'Todos los Usuarios de '+str(depto)
		}
	else:
		#Obtener todos los usuarios registrados en el sistema
		d_u = get_all_user()
		ctx = {'lista':d_u,
			   'h1':'Todos los Usuarios del sistema'
		}
	return render(request, 'GestionUser/index.html', ctx)

#vista para INICIAR SESIÓN
def entrar(request):
	user = request.user
	ctx = {}

	if request.method == 'GET' and 'next' in request.GET: #miramos si está la variables next para redirección
		ctx['next'] = request.GET['next'] #guardamos la variables next para enviar al template
	#Comprobamos si el usuario está autenticado!
	if user.is_authenticated():
		return redirect( get_url_redir(request) )
	#Si el usuario envía datos por POST para su autenticación
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST) #usamos el formulario de auth de django
		if form.is_valid(): #si el form es válido obtenemos el usuario y password
			u = form.cleaned_data['username']
			p = form.cleaned_data['password']
			user = authenticate(username=u, password=p) #comprobamos usuario y contraseña
			if user is not None and user.is_active: #si existe y si está activo
				login(request, user) #logueado en las sesion de django
				# dependiendo del depto al q pertenece el user así se redirecionará
				return redirect( get_url_redir(request) )
		else:
			ctx['form'] = form #guardamos el form con los datos resultantes de la validación
			return render(request, 'GestionUser/entrar.html', ctx)

	form = AuthenticationForm() #un formulario sin datos del POST
	ctx['form'] = form #guardamos un form limpio
	return render(request, 'GestionUser/entrar.html', ctx)

#Vista para cerrar la sesión
def salir(request):
	logout(request)
	request.user = None
	return redirect('/sgpc/cuentas/entrar/')