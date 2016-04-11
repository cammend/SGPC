from django.shortcuts import render, redirect
from .forms import UsuarioForm
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import getDeptos, getTipos
from apps.Deptos.models import Departamento, DeptoUser
from .funciones import *

ROOT = 0
ADMIN = 1
NORMAL = 2


# VISTAS

def eliminarSeguridad(request):
	ctx = {}
	if request.method == 'POST':
		id = request.POST['usuario']
		d_u = get_depto_user(get_user_by_id(id))[0]
		ctx['usuario'] = d_u.usuario
		ctx['depto'] = d_u.depto
	else:
		id = request.GET['usuario']
		Usuario.objects.filter(id=id).delete()
		return redirect('/sgpc/cuentas/eliminar/')
	return render(request, 'GestionUser/eliminar_seguro.html', ctx)

@login_required
def eliminarUsuario(request):
	users = []
	ctx = {}
	if request.user.tipoUser == ROOT: #si el usuario es ROOT
		#Obtener todos los usuarios ADMIN
		users = get_admin_users() #devuelve todos los ADMIN
		ctx['is_root'] = True
	elif request.user.tipoUser == ADMIN: #si el usuario es ADMIN
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
			ctx = {'titulo': 'Guardado', 'h3': 'Usuario Guardado!'}
			return render(request, 'GestionUser/estado.html', ctx)
		else:
			ctx['form'] = form
			
	return render(request, 'GestionUser/crear_usuario.html', ctx)

@login_required
def index(request):
	tipo = request.user.tipoUser
	ctx = {}
	if tipo == NORMAL:
		return redirect('/sgpc/depto/home/')
	elif tipo == ADMIN:
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
	if user.is_authenticated and not user.is_anonymous:
		if user.tipoUser == ROOT:
			return redirect('/sgpc/cuentas/')
		else:
			return redirect('/sgpc/depto/home/')
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST) #usamos el formulario de auth de django
		if form.is_valid(): #si el form es válido obtenemos el usuario y password
			u = form.cleaned_data['username']
			p = form.cleaned_data['password']
			user = authenticate(username=u, password=p) #comprobamos usuario y contraseña
			if user is not None and user.is_active: #si existe y si está activo
				login(request, user) #logueado en las sesion de django
				# dependiendo del depto al q pertenece el user así se redirecionará
				return redirect('/sgpc/depto/home/')
		else:
			ctx = {'form':form} #guardamos el form con los datos resultantes de la validación
			return render(request, 'GestionUser/entrar.html', ctx)
	form = AuthenticationForm() #un formulario sin datos del POST
	ctx = {'form':form} #guardamos un form limpio
	return render(request, 'GestionUser/entrar.html', ctx)

def salir(request):
	logout(request)
	request.user = None
	return redirect('/sgpc/cuentas/entrar/')