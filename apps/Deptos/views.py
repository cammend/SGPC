from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView
from django.views.generic.list import ListView
from .models import Departamento
from apps.Estado.funciones import *
from .funciones import *

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
	ctx['usuario'] = user
	ctx['depto'] = get_depto_of_user(user)
	if exist_depto_in_state(user): #si el depto existe en el modelo 'EstadoDepto'
		ctx['gestionar'] = True
		ctx['pedidos_gestion'] = get_pedidos_in_my_depto(request.user)
	return render(request, 'Deptos/depto.html', ctx)

class VerDeptos(ListView):
	model = Departamento
	fields = ['nombre']
	template_name = 'Deptos/lista_deptos.html'


#Vista para crear un nuevo Departamento
class NuevoDepto(CreateView):
	model = Departamento
	fields = ['nombre']
	template_name = 'Deptos/nuevo_depto.html'
	success_url = '/sgpc/depto/lista/'

	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		user = self.request.user
		if user.es_root():
			return super(NuevoDepto, self).dispatch(*args, **kwargs)
		return redirect(user.get_url_home())