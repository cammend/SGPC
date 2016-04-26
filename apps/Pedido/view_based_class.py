from django.shortcuts import render, redirect
from .funciones import *
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Pedido, Producto
from .forms import *
from apps.Deptos.funciones import *
from apps.Estado.models import EstadoDepto, Estado
from apps.Cotizacion.models import Cotizacion, ProductosCotizados
from django.db.models import Sum, F, Avg, FloatField, ExpressionWrapper
from apps.Deptos.models import Departamento
from apps.VISTAS.view_based_class import *
from apps.Transicion.forms import *


#**************************************************************
#Las siguientes son clases que ya se les aplica un "Modelo Pedido"
class BasePedidoListView(BaseModeloListView):
	model = Pedido
	error = False
	pedidos_para_gestionar = False
	pedidos_no_publicados = False

	#Devuelve 2 tipos de listas de "Pedidos"... los "No Publicados" y los "Para Gestionar"
	def get_queryset(self):
		user = self.request.user
		depto = user.get_depto
		try:
			users = DeptoUser.objects.filter(depto=depto).values('usuario')
			if self.pedidos_no_publicados:
				no_public = Estado.objects.filter(id=1) #Estado no publicado
				print(no_public)
				pedidos = Pedido.objects.filter(usuario=users, estado=no_public)
				print(pedidos)
				return pedidos
			elif self.pedidos_para_gestionar:
				estados = EstadoDepto.objects.filter(depto=depto).values('estado')
				return Pedido.objects.filter(estado=estados)
		except:
		 	pass
		error = True
		return None

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		if self.error:
			ctx = {'titulo':'Error', 'titulo_msg': 'Producto no encontrado'}
			ctx['url_redir'] = user.get_url_home()
			return render(self.request, 'GestionUser/info.html', ctx)

		return super(BaseModeloListView, self).dispatch(*args, **kwargs)


#Ésta clase es para que se pueda ver un detalle de un Pedido
class BasePedidoDetailView(BaseModeloDetailView, SeguridadPedidoEstado):
	#Variables obligatorias del DetailView
	template_name = 'Pedido/detalle_pedido.html'
	model = Pedido


class BasePedidoProductoDetailView(BasePedidoDetailView):
	id_estado = 1 #Para seguridad, ESTADO NO PUBLICADO
	#Aca es para enviar los productos del pedido también.
	def get_context_data(self, **kwargs):
		context = super(BasePedidoProductoDetailView, self).get_context_data(**kwargs)
		pedido = kwargs['object']
		productos = Producto.objects.filter(pedido=pedido)
		products = productos.annotate( total=ExpressionWrapper( F('cantidad')*F('precio'), output_field=FloatField() ) )
		context['productos'] = products
		if self.id_estado == 1:
			context['editar_pedido'] = True
		return context

#Esta clase muestra un formulario para gestionar el pedido... sólo si se puede según ciertos criterios
class BasePedidoGestionDetailView(BasePedidoProductoDetailView):
	form = FormGestionar()
	choices_est_act = None
	choices_est_sig = None
	gestionar = False

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		print("PEDIDO GESTION")
		#Sacamos el estado del pedido
		id = kwargs['id']
		pedido = Pedido.objects.get(id=id)
		#Asignamos un template dependiendo el depto
		if self.template_name is None:
			self.template_name = get_template_for_depto(user.get_depto())
		#Comprobamos q se pueda gestionar
		self.gestionar = pedido_se_puede_gestionar(pedido)
		if self.gestionar:
			#Creamos las varibles para el formulario de gestión
			self.choices_est_act = [(pedido.estado.id, pedido.estado.nombre)]
			est_tran = Transicion.objects.filter(estadoActual=pedido.estado)
			self.choices_est_sig = make_choices_from_tran(est_tran)
		return super(BasePedidoGestionDetailView, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		user = self.request.user
		context = super(BasePedidoGestionDetailView, self).get_context_data(**kwargs)
		context['form_depto'] = get_form_for_depto(user.get_depto())
		if self.gestionar:
			self.form.fields['est_act'].choices = self.choices_est_act
			self.form.fields['est_sig'].choices = self.choices_est_sig
			context['form_gestion'] = self.form
		return context

class BasePedidoUpdateView(BaseModeloUpdateView, SeguridadPedidoEstado):
	id_estado = 1 #Para seguridad, ESTADO NO PUBLICADO
	model = Pedido
	no_publicado = True #Comprueba si es no publicado, si se cambia a False, en estos momentos dará error.

	def dispatch(self, *args, **kwargs):
		#Aca se regresa al detalle del pedido por success_url
		self.success_url = recortar_url(self.request.path, 5)
		return super(BasePedidoUpdateView, self).dispatch(*args, **kwargs)


#un pedido se puede borrar si está como no publicado, por defecto se borra cualquier pedido
class BasePedidoDeleteView(BaseModeloDeleteView, SeguridadPedidoEstado):
	id_estado = 1 #Para seguridad, ESTADO NO PUBLICADO
	model = Pedido
	success_url = '/sgpc/depto/pedido/no_publicado/'

#Crear un nuevo pedido
class BasePedidoCreateView(BaseModeloCreateView):
	model = Pedido
	pedido = None
	template_render = 'Pedido/info.html'
	ctx = {'titulo':'Creado', 'titulo_msg':'Pedido Creado', 'msg':'Para agregar otro'}

	def form_valid(self, form):
		pedido = form.save(commit=False)
		pedido.usuario = self.request.user
		no_public = Estado.objects.get(id=1) #no publicado
		pedido.estado = no_public
		pedido.save()
		#Para que redireccione directamente al detalle del pedido
		self.success_url = '/sgpc/depto/pedido/no_publicado/'+str(pedido.id)+'/'
		if self.success_url:
			return redirect(self.success_url)
		return render(self.request, self.template_render, self.ctx)

	def get_context_data(self, **kwargs):
		context = super(BasePedidoCreateView, self).get_context_data(**kwargs)
		context['pedido'] = self.pedido
		return context

	
#FIN MODELO PEDIDO
#--------------------------------------------------------------

"""
TODOS LOS PRODUCTOS FILTRADOS POR estado
"""

#Clase de seguridad que deja pasar todos los pedidos "No Publicados"
class ProductoNoPublicadoView(SeguridadProductoEstado):
	id_estado = 1
	ctx = None

	def dispatch(self, *args, **kwargs):
		self.success_url = recortar_url(self.request.path, 5)
		self.ctx = {'titulo':'Error', 'titulo_msg':'Producto no encontrado'}
		estado = Estado.objects.get(id=self.id_estado)
		self.ctx['msg'] = 'Estado: "'+str(estado)+'".'
		self.ctx['url_redir'] = self.request.user.get_url_home()
		return super(ProductoNoPublicadoView, self).dispatch(*args, **kwargs)

"""
TODOS LOS PRODUCTOS Y ACCESO A DATOS (UPDATE, DELETE, CREATE, LIST)
"""
#Clase para actualizar un producto
class BaseProductoUpdateView(BaseModeloUpdateView, ProductoNoPublicadoView):
	model = Producto

	def dispatch(self, *args, **kwargs):
		self.success_url = recortar_url(self.request.path, 5)
		return super(BaseProductoUpdateView, self).dispatch(*args, **kwargs)


class BaseProductoDeleteView(BaseModeloDeleteView, ProductoNoPublicadoView):
	model = Producto

	def dispatch(self, *args, **kwargs):
		self.success_url = recortar_url(self.request.path, 5)
		return super(BaseProductoDeleteView, self).dispatch(*args, **kwargs)


#FALTA QUE SE GUARDE AUTOMÁTICAMENTE LA SUMA DE LOS PRODUCTOS EN EL PEDIDO
class BaseProductoCreateView(BaseModeloCreateView):
	model = Producto
	id_pedido = None
	url_redir = None
	pedido = None
	template_render = 'Pedido/info.html'
	ctx = {'titulo':'Creado', 'titulo_msg':'Producto Guardado', 'msg':'Para agregar otro'}

	#Con éste método nos aseguramos de agregar un producto sólo a un pedido de nuestro depto
	#y también que esté en estado "no publicado"
	def dispatch(self, *args, **kwargs):
		user = self.request.user
		depto = user.get_depto()
		self.id_pedido = kwargs['id']
		#para q redireccione a la vista pedido
		path = self.request.path
		self.success_url = recortar_url(path,5)
		try:
			self.pedido = Pedido.objects.get(id=self.id_pedido)
			depto_p = self.pedido.usuario.get_depto()
			self.url_redir = self.request.path
			no_public = Estado.objects.get(id=1) #No Publicado
			if depto_p == depto and self.pedido.estado == no_public:
				return super(BaseProductoCreateView, self).dispatch(*args, **kwargs)
		except:
		 	pass
		ctx = {'titulo':'Error', 'titulo_msg':'Pedido no encontrado.'}
		ctx['url_redir'] = user.get_url_home()
		return render(self.request, 'GestionUser/info.html', ctx)

	def form_valid(self, form):
		producto = form.save(commit=False)
		producto.pedido = self.pedido
		producto.save()
		#total = self.pedido.total
		#total = total + (producto.precio * producto.cantidad)
		#Pedido.objects.filter(id=self.id_pedido).update(total=total)

		if self.success_url:
			return redirect(self.success_url)
		return render(self.request, self.template_render, self.ctx)

	def get_context_data(self, **kwargs):
		context = super(BaseProductoCreateView, self).get_context_data(**kwargs)
		context['pedido'] = self.pedido
		return context