from django.shortcuts import render,redirect
from .models import Cotizacion
from apps.Pedido.models import Pedido
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .forms import formCotizacion

# Create your views here.

@login_required
def ListarCotizaciones(request):
	user = request.user
	ctx = {'titulo':'Gestión'}
	if user.es_root(): #si es usuario ROOT... no devería ver ésta vista
		return redirect('/sgpc/cuentas/') #y lo redireccionamos

	id = 1
	pedido = Pedido.objects.get( id = id) 
	lista = Cotizacion.objects.filter(pedido = pedido)
	ctx['lista_cotizaciones'] = lista
	return render(request,'cotizaciones/cotizaciones.html',ctx)

#Vista para ingresar cotizacion
@login_required
def IngresarCotizacion(request):
	#user = request.user
	#ctx = {'titulo':'Gestión'}
	#if user.es_root(): #si es usuario ROOT... no devería ver ésta vista
		#return redirect('/sgpc/cuentas/') #y lo redireccionamos
	
	form = formCotizacion()
	ctx = {'form': form}
	if request.method == 'POST':
		form = formCotizacion(request.POST)
		ctx['form'] = form
		if form.is_valid():
			form.save()
		else:
			ctx['form'] = form
			
	return render(request,'cotizaciones/crear_cotizaciones.html',ctx )




