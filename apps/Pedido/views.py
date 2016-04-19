from django.shortcuts import render, redirect
from .funciones import *
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView
from .models import Pedido, Producto
from .forms import FormPedido, FormProducto
from apps.Deptos.funciones import *

# Create your views here.
def verPedidos(request):
	user = request.user
	lista = get_all_pedidos_by_depto(user)
	ctx = {'lista': lista}
	return render(request, 'Pedido/ver_pedidos.html', ctx)

class DetallePedido(DetailView):
	model = Pedido
	template_name = 'probar_listas.html'
	slug_url_kwarg = 'id'
	slug_field = 'id'

def nuevoPedido(request):
	user = request.user
	form = FormPedido()
	ctx = {'titulo':'Nuevo Pedido', 'h2':'Nuevo Pedido'}
	ctx['form'] = form
	if request.method == 'POST':
		form = FormPedido(data=request.POST)
		if form.is_valid():
			pedido = form.save(user)
			request.session['id_pedido'] = pedido.id
			return redirect('/sgpc/depto/producto/nuevo/')
		else:
			ctx['form'] = form
	return render(request, 'Pedido/nuevo_pedido.html', ctx)

def nuevoProducto(request):
	user = request.user
	form = FormProducto()
	ctx = {'form': form}
	id_pedido = None
	#obteniendo el pedido
	if 'id_pedido' in request.session: id_pedido = request.session['id_pedido']
	else: redirect('/sgpc/depto/pedido/nuevo/')

	pedido = Pedido.objects.get(id=id_pedido)
	ctx['pedido'] = pedido

	if request.method == 'POST':
		form = FormProducto(data=request.POST)
		if form.is_valid():
			form.save(pedido)
		else:
			ctx['form'] = form
	return render(request, 'Pedido/nuevo_producto.html', ctx)

def finalizarPedido(request):
	id = request.session.pop('id_pedido',None)
	print(id)
	ctx = {'titulo': 'Guardado',
		   'titulo_msg': 'Finalizado!',
		   'msg': 'Pedido finalizado!',
		   'url_redir': request.user.get_url_home()}
	return render(request, 'GestionUser/info.html', ctx)