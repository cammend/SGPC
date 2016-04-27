from django.shortcuts import render, redirect
from .funciones import *
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Pedido, Producto
from .forms import FormPedido, FormProducto
from apps.Deptos.funciones import *
from GestionUser.funciones import *
from GestionUser.models import Usuario
from apps.Estado.models import EstadoDepto, Estado
from apps.Cotizacion.models import Cotizacion, ProductosCotizados
from .view_based_class import *
from apps.Cotizacion.forms import *
from django.db.models import Sum, F, Avg, FloatField, ExpressionWrapper
#from apps.Transicion.forms import FormGestionar


def gestionarPedido(request):
	user = request.user
	id = request.POST['id']
	#Obtenemos las variables
	if request.method == 'POST':
		sig = request.POST['est_sig']
		if sig:
			pedido = Pedido.objects.get(id=id)
			est_act = Estado.objects.get(id=request.POST['est_act'])
			est_sig = Estado.objects.get(id=request.POST['est_sig'])
			transicion = Transicion.objects.get(estadoActual=est_act, estadoSiguiente=est_sig)
			#guardamos el historial
			historial = HistorialTransicion()
			historial.pedido = pedido
			historial.usuario = user
			historial.transicion = transicion
			historial.save()
			#cambiamos de estado al pedido
			Pedido.objects.filter(id=id).update(estado=est_sig)

			ctx = {'titulo':'Pedido Gestionado', 'titulo_msg': 'Pedido gestionado exitosamente.'}
			ctx['url_redir'] = user.get_url_home()
			return render(request, 'GestionUser/info.html', ctx)
		else:
			ctx = {'titulo':'Error', 'titulo_msg':'Formulario no válido', 'msg':'Debe seleccionar una opción.'}
			ctx['url_redir'] = '/sgpc/depto/pedido/no_publicado/'+str(id)+'/'
			return render(request, 'GestionUser/info.html', ctx)

	ctx = {'titulo':'Error', 'titulo_msg':'No hay datos', 'url_redir':user.get_url_home()}
	return render(request, 'GestionUser/info.html', ctx)



#Listar Pedidos no publicados
class ListarPedidosNoPublicados(BasePedidoListView):
	pedidos_no_publicados = True
	template_name = 'Pedido/pedidos_no_publicados.html'

#Detalle de un pedido no publicado
class DetallePedidoNoPublicado(BasePedidoGestionDetailView):
	template_name = 'Pedido/detalle_pedido.html'
	pedido_no_publico = True

#Editar un pedido no publicado
class EditarPedidoNoPublicado(BasePedidoUpdateView):
	fields = ['justificacion','fecha']
	template_name = 'Pedido/editar_pedidos.html'
	nombre_actividad = 'Se editó un pedido no publicado'

#Eliminar un pedido no publicado
class EliminarPedidoNoPublicado(BasePedidoDeleteView):
	no_publicado = True
	nombre_actividad = 'Se eliminó un pedido'

#Crear un nuevo pedido
class CrearPedidoNoPublicado(BasePedidoCreateView):
	template_name = 'Pedido/nuevo_pedido.html'
	fields = ['justificacion', 'fecha']

#Agregar un nuevo producto al pedido
class NuevoProducto(BaseProductoCreateView):
	model = Producto
	fields = ['descripcion', 'cantidad']
	template_name = 'Pedido/nuevo_producto.html'

#Eliminar un producto
class EliminarProductoNoPublicado(BaseProductoDeleteView):
	success_url = '/sgpc/depto/pedido/no_publicado/'

#Editar un producto
class EditarProductoNoPublicado(BaseProductoUpdateView):
	success_url = '/sgpc/depto/home/'
	fields = ['descripcion', 'cantidad']

class DetallePedidoGestionar(BasePedidoGestionDetailView):
	pedido_para_gestionar = True
	id_estado = 0
	template_name = None

def guardarRenglon(request, id):
	if request.method == 'POST':
		form = FormAsignaRenglon(request.POST)
		if form.is_valid():
			form.save()
			return redirect(recortar_url(request.path, 5))
			#pedido = Pedido.objects.filter(id=id_pedido)
			#pedido.update(renglon=request.POST[''])
		else:
			ctx = {'titulo': 'Error', 'titulo_msg': 'Form no válido'}
			return render(request, 'GestionUser/info.html', ctx)

	pedido = Pedido.objects.get(id=id)
	prods = Producto.objects.filter(pedido=pedido)
	ctx = {}
	ctx['productos'] = prods
	form = FormAsignaRenglon()
	form.fields['renglon'].label=''
	ctx['form'] = form
	return render(request, 'Pedido/asignar_presupuesto.html', ctx)

def guardarCotizacion(request, id):
#Variables
	estado = Estado.objects.get(id=4) #Aprobado por gerente
	pedido = Pedido.objects.get(id=id)
#Seguridad a nivel de usuario
	seg_user = SegUser(request, False, True, True)
	if not seg_user.es_valido(): return seg_user.get_render()
#Seguridad a nivel del Pedido
	seg_pedido = SegPedido(request, estado=estado, pedido=pedido)
	if seg_pedido.pedido is not None:
		if not seg_pedido.es_valido(): return seg_pedido.get_render()
#Continuamos... guardando varibles necesarias
	request.session['url_cot'] = request.path
	pedido = Pedido.objects.get(id=id)
	productos = Producto.objects.filter(pedido=pedido)
	cotizaciones = Cotizacion.objects.filter(pedido=pedido)
#Comprobando y guardando el form
	if request.method == 'POST':
		form = FormCotizacion(request.POST)
		if form.is_valid():
			form.save(pedido)
		else:
			ctx = {'titulo': 'Error', 'titulo_msg': 'Form no válido'}
			return render(request, 'GestionUser/info.html', ctx)
#Retornando un form vacío
	form = FormCotizacion()
	ctx = {'form': form, 'pedido':pedido, 'productos':productos, 'cotizaciones':cotizaciones}
	ctx['url_back'] = recortar_url(request.path, 5)
	return render(request, 'Pedido/agregar_cotizacion.html', ctx)

def guardarProductosCotizados(request, id):
#Variables
	estado = Estado.objects.get(id=4) #Aprobado por gerente
	pedido = Cotizacion.objects.get(id=id).pedido
#Seguridad a nivel de usuario
	seg_user = SegUser(request, False, True, True)
	if not seg_user.es_valido(): return seg_user.get_render()
#Seguridad a nivel del Pedido
	seg_pedido = SegPedido(request, estado=estado, pedido=pedido)
	if seg_pedido.pedido is not None:
		if not seg_pedido.es_valido(): return seg_pedido.get_render()
#Continuacion... guardamos variables necesarias
	cotizacion = Cotizacion.objects.get(id=id)
	pedido = cotizacion.pedido
	if request.method == 'POST':
		form = FormProductoCotizado(request.POST)
		if form.is_valid():
			id_cot = request.POST['id_cot']
			form.save(cotizacion)
		else:
			ctx = {'titulo': 'Error', 'titulo_msg': 'Form no válido'}
			return render(request, 'GestionUser/info.html', ctx)
#Guardando variables extras al queryset
	productos = ProductosCotizados.objects.filter(cotizacion=cotizacion)
	if productos:
		productos = productos.annotate( total=ExpressionWrapper( F('cantidad')*F('precio'), output_field=FloatField() ) )
#Retornamos un form vacío, y mandamos variables al context
	form = FormProductoCotizado()
	form.fields['producto'].choices = get_choice_for_cot(cotizacion)
	ctx = {'form': form, 'pedido':pedido, 'productos':productos, 'cotizacion':cotizacion}
	ctx['url_editar'] = recortar_url(request.path, 6)
	ctx['url_eliminar'] = recortar_url(request.path, 6) + 'eliminar/'
	if 'url_cot' in request.session:
		ctx['url_back'] = request.session['url_cot']
	else:
		ctx = {'titulo':'Error', 'titulo_msg': 'Acceso por url', 'msg':'Has intentado acceder a la página directamente por url.'}
		return render(request, 'GestionUser/info.html', ctx)
	return render(request, 'Pedido/pedido_de_cotizacion.html', ctx)

