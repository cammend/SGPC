from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .models import Departamento, DeptoUser
from apps.Estado.funciones import *

# Create your views here.

#Vista para mostrar una página correspondiente para un usuario logueado!
@login_required
def home(request):
	user = request.user
	ctx = {'titulo':'Gestión'}
	if user.es_root(): #si es usuario ROOT... no devería ver ésta vista
		return redirect('/sgpc/cuentas/') #y lo redireccionamos
	elif user.es_admin():
		ctx['is_admin'] = True

	#Se crea la página para la gestión de los pedidos dependiendo el Depto
	d_u = DeptoUser.objects.filter(usuario=request.user)[0] #obtenemos el usuario y el depto al q pertenece
	ctx['user_depto'] = d_u
	ctx['usuario'] = d_u.usuario
	ctx['depto'] = d_u.depto
	if exist_depto_in_state(request.user): #si el depto existe en el modelo 'EstadoDepto'
		ctx['gestionar'] = True
		ctx['pedidos_gestion'] = get_pedidos_in_my_depto(request.user)
	return render(request, 'Deptos/depto.html', ctx)


#Vista para crear un nuevo Departamento
class NuevoDepto(CreateView):
	model = Departamento
	fields = '__all__'
	template_name = 'Deptos/nuevo_depto.html'