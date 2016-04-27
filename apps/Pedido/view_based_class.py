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
		cotizaciones = Cotizacion.objects.filter(pedido=pedido)
		self.request.session['url_cot_deptos'] = self.request.path
		context['cotizaciones'] = cotizaciones
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


"""""
PRUEBAS
"""""

#Clase de seguridad a nivel de tipo de usuario
class SegUser():
	user_root = False
	user_admin = False
	user_normal = False
	template_render = 'GestionUser/info.html'
	ctx = {'titulo':'Error', 'titulo_msg':'Página no encontrada'}
	request = None
	user = None

	def __init__(self, request, user_root=False, user_admin=False, user_normal=False):
		self.user_root = user_root
		self.user_admin = user_admin
		self.user_normal = user_normal
		self.request = request
		self.user = request.user

	def is_root(self, user):
		return (user.es_root() and self.user_root)
	def is_admin(self, user):
		return (user.es_admin() and self.user_admin)
	def is_normal(self, user):
		return (user.es_normal() and self.user_normal)

	def es_valido(self):
		user = self.request.user
		return ( self.is_root(user) or self.is_admin(user) or self.is_normal(user) )

	def get_render(self):
		return render(self.request, self.template_render, self.ctx)

#Funciones generales de pedido con (user, depto y estado)
def pedido_a_user(pedido, user):
	if pedido and user:
		if user == pedido.usuario: return True
	print("pedido a user: False")
	return False
def pedido_a_depto(pedido, depto):
	if pedido and depto:
		if depto == pedido.usuario.get_depto(): return True
	print("pedido a depto: False")
	return False
def pedido_en_estado(pedido, estado):
	if pedido and estado:
		if pedido.estado == estado: return True
	print("pedido a estado: False")
	return False

#Clase de seguridad a nivel de pedido
class SegPedido():
	estado = None #Seguridad por estado
	user = None #Seguridad por usuario
	depto = None #Seguridad por depto
	pedido = None #Modelo a verificar
	request = None
	template_render = 'GestionUser/info.html'
	ctx = {'titulo':'Error', 'titulo_msg':'Modelo no encontrado'}

	def __init__(self, request, estado=None, user=None, depto=None, pedido=None):
		self.estado = estado
		self.user = user
		self.depto = depto
		self.pedido = pedido
		self.request = request

	def a_user(self): #POR USUARIO
		return pedido_a_user(self.pedido, self.user)
	def a_depto(self): #POR DEPTO
		return pedido_a_depto(self.pedido, self.depto)
	def en_estado(self): #POR ESTADO
		return pedido_en_estado(self.pedido, self.estado)

	def _get_queryset(self):
		if self.user:
			if self.estado:
				return Pedido.objects.filter(usuario=self.usuario, estado=self.estado)
			return Pedido.objects.filter(usuario=self.usuario)
		elif self.depto:
			users = DeptoUser.objects.filter(depto=self.depto).values('usuario')
			if self.depto:
				print(users)#DEBUG
				return Pedido.objects.filter(usuario=users, estado=self.estado)
			return Pedido.objects.filter(usuario=users)
		elif self.estado:
			return Pedido.objects.filter(estado=self.estado)
		print("DEBUG SegPedido: Se están retornando todos los pedidos.")
		return Pedido.objects.all()

	def es_valido(self):
		if self.pedido is None:
			print("DEBUG SegPedido: El pedido no debe ser None.")
		if self.a_user() or self.a_depto() or self.en_estado():
			return True
		return False

	def get_render(self):
		return render(self.request, self.template_render, self.ctx)


class BasePedidoProtegido(View):
	queryset = None
	#Variables para SegUser
	user_root = False
	user_admin = False
	user_normal = False
	#Variables para SegPedido
	estado = None #Seguridad por estado
	user = None #Seguridad por usuario
	depto = None #Seguridad por depto
	pedido = None #Modelo a verificar


	def seguridad(self, request):
		#Seguridad a nivel de usuario
		seg_user = SegUser(self.request, self.user_root, self.user_admin, self.user_normal)
		if not seg_user.es_valido(): return seg_user.get_render()
		#Seguridad a nivel del Pedido
		seg_pedido = SegPedido(self.request, self.estado, self.user, self.depto, self.pedido)
		if seg_pedido.pedido is not None:
			if not seg_pedido.es_valido(): return seg_pedido.get_render()
		else:
			self.queryset = seg_pedido._get_queryset()
		#Si no hubo ningún fallo de seguridad...
		return False

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		#Aplicando la seguridad
		seguridad = self.seguridad(self.request)
		if seguridad: return seguridad
		#Si no hay ningún fallo de seguridad...
		return super(BasePedidoProtegido, self).dispatch(*args, **kwargs)


class ListarTodosLosPedidos(BasePedidoProtegido, ListView):
	model = Pedido
	template_name = 'Genericas/list.html'
	user_admin = True
	user_normal = True
	estado = Estado.objects.filter(id=1)

class DetalleDePedido(BasePedidoProtegido, UpdateView):
	model = Pedido
	slug_url_kwarg = 'id'
	slug_field = 'id'
	template_name = 'Genericas/update.html'
	user_admin = True
	user_normal = True
	estado = Estado.objects.filter(id=1)
	fields = ['fecha']
	pedido = None

	def dispatch(self, *args, **kwargs):
		self.pedido = Pedido.objects.get(id=kwargs['id'])
		return super(DetalleDePedido, self).dispatch(*args, **kwargs)

class BaseCotizacionProtegida(BasePedidoProtegido):
	model = Cotizacion
	slug_url_kwarg = 'id'
	slug_field = 'id'
	fields = ['proveedor','fecha_cotizacion','fecha_entrega']
	#Variables de SegUser
	user_admin = True
	user_normal = True
	#Variables de SegPedido
	estado = Estado.objects.get(id=4) #Aprobado por gerente
	depto = None
	pedido = None
	success_url = None

	def dispatch(self, *args, **kwargs):
		self.depto = self.request.user.get_depto()
		if self.success_url is None:
			self.success_url = self.request.path + 'pedido/'
		try:
			print("DEBUG BCP: ANTES")
			cotizacion = Cotizacion.objects.get(id=kwargs['id'])
			print("DEBUG BCP: DESPUES")
			self.pedido = cotizacion.pedido
			print(self.pedido)
		except:
			self.pedido = None
		return super(BaseCotizacionProtegida, self).dispatch(*args, **kwargs)

class EditarCotizacion(BaseCotizacionProtegida, UpdateView):
	template_name = 'Genericas/update.html'

	def dispatch(self, *args, **kwargs):
		self.success_url = self.request.path + 'pedido/'
		return super(BaseCotizacionProtegida, self).dispatch(*args, **kwargs)

class EliminarCotizacion(BaseCotizacionProtegida, DeleteView):
	template_name = 'Genericas/delete.html'
	success_url = '/sgpc/depto/home/'

class AsignarPrioridadCot(BaseCotizacionProtegida, UpdateView):
	template_name = 'cotizaciones/actualizar_cotizacion.html'
	estado = Estado.objects.get(id=5)
	fields = ['prioridad', 'cancelada']
	cotizacion = None

	def dispatch(self, *args, **kwargs):
		self.cotizacion = Cotizacion.objects.get(id=kwargs['id'])
		self.success_url = self.request.session['url_cot_deptos']
		return super(AsignarPrioridadCot, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(AsignarPrioridadCot, self).get_context_data(**kwargs)
		context['cotizacion'] = self.cotizacion
		productos = ProductosCotizados.objects.filter(cotizacion=self.cotizacion)
		productos = productos.annotate( total=ExpressionWrapper( F('cantidad')*F('precio'), output_field=FloatField() ) )
		context['productos'] = productos
		return context

class ListarPedidosParaComprar(BasePedidoProtegido, ListView):
	template_name = 'Pedido/pedidos_por_comprar.html'
	estado = Estado.objects.get(id=6)
	model = Pedido
	user_admin = True
	user_normal = True

	def dispatch(self, *args, **kwargs):
		return super(ListarPedidosParaComprar, self).dispatch(*args, **kwargs)

class DetallePedidoParaComprar(BaseCotizacionProtegida, DetailView):
	slug_url_kwarg = 'id'
	slug_field = 'id'
	template_name = 'Pedido/detalle_pedido_comprar.html'
	__pedido = None
	#Variables para SegUser
	user_admin = True
	user_normal = True
	#Variables para SegPedido
	estado = Estado.objects.get(id=6)
	model = Pedido

	def get_context_data(self, **kwargs):
		context = super(DetallePedidoParaComprar, self).get_context_data(**kwargs)
		cotizaciones = Cotizacion.objects.filter(pedido=self.__pedido).order_by('prioridad')
		#print("PEDIDO__: "+str(self.pedido))
		#print("COT: "+str(cotizaciones))
		context['pedido'] = self.__pedido
		context['cotizaciones'] = cotizaciones
		return context

	def dispatch(self, *args, **kwargs):
		self.__pedido = Pedido.objects.get(id=kwargs['id'])
		#print("ID: "+str(kwargs['id']))
		#print("PEDIDO: "+str(self.pedido))
		#self.success_url = self.request.session['url_cot_deptos']
		return super(DetallePedidoParaComprar, self).dispatch(*args, **kwargs)
