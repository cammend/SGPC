from django.shortcuts import render, redirect
from .forms import UsuarioForm
from .models import Usuario
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import getDeptos, getTipos
from apps.Deptos.models import Departamento

host = '/sgpc/'
cuentas = 'cuentas/'
deps = 'depto/'

#ésta función devuelve una lista con los deptos disponibles para el usuario ROOT o una lista
#con el depto al q pertenece un usuario ADMIN
def getListaDepto(usuario):
	dep = getDeptos().copy()
	print(dep)
	if usuario.tipoUser == 0: #si el usuario actual es ROOT
		query = Usuario.objects.filter(tipoUser=1).order_by('depto') #devuelve todos los usuarios ADMIN
		print(query)
		aux = 0
		for u in query:
			del dep[u.depto-aux] #eliminamos de la lista todos los ADMIN ya creadoss
			print(dep)
			aux += 1
	elif usuario.tipoUser == 1: #si el usuario actual es ADMIN
		dp = dep.pop(usuario.depto)
		dep = [dp]
	return dep

#devuelve una lista con un elemento que dice que tipo de usuario se va a crear
def getListaTipo(usuario):
	tip = getTipos().copy()
	dep = []
	if usuario.tipoUser == 0: #si el usuario actual es ROOT
		dp = tip.pop(1)
		dep = [dp]
	elif usuario.tipoUser == 1: #si el usuario actual es ADMIN
		dp = tip.pop(2)
		dep = [dp]
	return dep

# Create your views here.
@login_required
def crearUsuarioView(request):
	form = UsuarioForm()
	choices = getListaDepto(request.user)
	if not choices:
		return redirect(host+cuentas+'eliminar/')
	form.fields['departamento'].choices = choices
	form.fields['tipo'].choices = getListaTipo(request.user)
	if request.method == 'POST':
		form = UsuarioForm(data=request.POST)
		form.fields['departamento'].choices = getListaDepto(request.user)
		form.fields['tipo'].choices = getListaTipo(request.user)
		if form.is_valid():
			form.save()
			form = UsuarioForm()
			form.fields['departamento'].choices = getListaDepto(request.user)
			form.fields['tipo'].choices = getListaTipo(request.user)
	if request.user.tipoUser == 2: #si el usuario es NORMAL... redireccionamos
		return redirect(host+deps+'home/')
	ctx = {'form':form}
	return render(request, 'GestionUser/crear_usuario.html', ctx)

@login_required
def eliminarUsuarioView(request):
	users = []
	if request.method == 'POST':
		id = request.POST['usuario']
		Usuario.objects.filter(id=id).delete()

	if request.user.tipoUser == 0: #si el usuario es ROOT
		users = Usuario.objects.filter(tipoUser=1) #devuelve todos los ADMIN
	elif request.user.tipoUser == 1: #si el usuario es ADMIN
		users = Usuario.objects.filter(depto=request.user.depto, tipoUser=2) #devuelve todos lo users del mismo depto
	else:
		return redirect(host+deps)
	ctx = {'lista':users}
	print(request.user.depto)
	return render(request, 'GestionUser/eliminar_usuario.html', ctx)

@login_required
def crearUsuario(request):
	form = UsuarioForm()
	deptos = Departamento.objects.all()
	print(deptos)
	return render(request, 'GestionUser/eliminar_usuario.html')

def entrar(request):
	if request.method == 'POST':
		form = AuthenticationForm(data=request.POST) #usamos el formulario de auth de django
		if form.is_valid():
			u = form.cleaned_data['username']
			p = form.cleaned_data['password']
			user = authenticate(username=u, password=p) #comprobamos usuario y contraseña
			if user is not None and user.is_active: #si existe y si está activo
				login(request, user) #logueado en las sesion de django
				# dependiendo del depto al q pertenece el user así se redirecionará
				return redirect('/sgpc/depto/home/')
		else:
			ctx = {'form':form}
			return render(request, 'GestionUser/entrar.html', ctx)
	form = AuthenticationForm()
	ctx = {'form':form}
	return render(request, 'GestionUser/entrar.html', ctx)

def salir(request):
	logout(request)
	request.user = None
	return redirect('/sgpc/cuentas/entrar/')