from django.shortcuts import render, redirect
from .funciones import *
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from .models import Pedido, Producto
from .forms import FormPedido, FormProducto
from apps.Deptos.funciones import *
from GestionUser.funciones import *
from apps.Estado.models import EstadoDepto, Estado
from apps.Cotizacion.models import Cotizacion, ProductosCotizados

# Create your views here.
@login_required
def verPedidos(request):
	user = request.user
	if user.es_root(): return redirect(user.get_url_home)
	lista = get_all_pedidos_by_depto(user)
	lista_id = generate_list_of_id(lista)
	request.session['lista_id_pedido'] = lista_id
	ctx = {'lista': lista}
	return render(request, 'Pedido/ver_pedidos.html', ctx)


class DetallePedido(DetailView):
	model = Pedido
	template_name = 'probar_listas.html'
	slug_url_kwarg = 'id'
	slug_field = 'id'

@login_required
def nuevoPedido(request):
	user = request.user
	if user.es_root(): return redirect(user.get_url_home)
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

@login_required
def nuevoProducto(request):
	user = request.user
	if user.es_root(): return redirect(user.get_url_home)
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

@login_required
def finalizarPedido(request):
	user = request.user
	if user.es_root(): return redirect(user.get_url_home)
	id = request.session.pop('id_pedido',None)
	print(id)
	ctx = {'titulo': 'Guardado',
		   'titulo_msg': 'Finalizado!',
		   'msg': 'Pedido finalizado!',
		   'url_redir': request.user.get_url_home()}
	return render(request, 'GestionUser/info.html', ctx)

@login_required
def detallePedido(request, id):
	user = request.user
	ctx = {}
	if user.es_root(): return redirect(user.get_url_home)
	depto_u = get_depto_of_user(user)
	pedido = Pedido.objects.get(id=id)
	depto_p = get_depto_of_pedido(pedido)
	if depto_u == depto_p:
		list_model = request.session['lista_id_pedido']
		productos = Producto.objects.filter(pedido=pedido)
		ctx['pedido'] = pedido
		ctx['productos'] = productos
		ctx['next'] = get_next_of_list_model(id, list_model)
		ctx['back'] = get_back_of_list_model(id, list_model)
	return render(request, 'Pedido/detalle_pedido.html', ctx)

class EditarProducto(UpdateView):
	model = Producto
	fields = ['descripcion', 'cantidad', 'precio']
	template_name = 'Pedido/editar_pedido.html'
	slug_url_kwarg = 'id'
	slug_field = 'id'
	success_url = '/sgpc/depto/pedido/ver/'

def gestionarPedido(request, id):
	user = request.user
	ctx = {}
	pedido = Pedido.objects.get(id=id)
	estado_pedido = pedido.estado
	estado_depto  = EstadoDepto.objects.get(depto=user.get_depto()).estado
	if estado_pedido == estado_depto: #si el pedido corresponde al depto
		estados = Estado.objects.all()
		if estado_depto == estados[0]: #NO PUBLICADO
			pass
		elif estado_depto == estados[1]: #PUBLICADO
			pass
		elif estado_depto == estados[2]: #CON PRESUPUESTO ASIGNADO
			pass
		elif estado_depto == estados[3]: #APROBADO POR GERENTE
			pass
		elif estado_depto == estados[4]: #COTIZADO
			pass
		elif estado_depto == estados[5]: #CON COTIZACIONES ORDENADAS
			pass
		elif estado_depto == estados[6]: #CON COTIZACION ELEGIDA
			if request.method == 'POST':
				if 'id_estado' in request.POST:
					id_estado = request.POST['id_estado']
					gestionar_presupuesto(id, id_estado)
					ctx['titulo'] = 'Gestionado'
					ctx['titulo_msg'] = 'Estado Cambiado'
					ctx['url_redir'] = user.get_url_home()
					return render(request, 'GestionUser/info.html', ctx)
			else:
				ctx = gestion_presupuesto(id)
			return render(request, 'Gestion/cotizacion_elegida.html', ctx)
		elif estado_depto == estados[7]: #COMPRADO
			pass
		elif estado_depto == estados[8]: #EN ALMACEN
			pass
		elif estado_depto == estados[9]: #RETIRADO DE ALMACEN
			pass
		elif estado_depto == estados[10]: #CANCELADO
			pass

	return redirect(user.get_url_home())