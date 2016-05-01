from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.views.generic.base import View
from apps.Pedido.models import Pedido, Producto
from apps.Deptos.models import Departamento
from apps.Estado.models import Estado, EstadoDepto
from GestionUser.models import DeptoUser, normalizar_url
from apps.Cotizacion.models import Cotizacion, ProductosCotizados
from apps.Transicion.forms import FormGestionar, choice_actual, choice_siguiente
from apps.Transicion.models import *
from apps.Pedido.forms import FormRenglon
from apps.Cotizacion.forms import FormProductoCotizado

# Create your views here.

ps = [
	"El pedido sólo se puede publicar si tiene por lo menos un producto asignado",
	"El pedido se puede gestionar sólo si se le asignó el renglón presupuestario a cada producto del pedido.",
	"El pedido se puede aceptar o cancelar.",
	"El pedido se puede gestionar si por lo menos tiene una cotización asignada.",
	"El pedido se puede gestionar hasta que cada cotización tenga una prioridad asignada.",
	"El pedido se puede gestionar hasta que se elija una cotización para la compra.",
	"El pedido está listo para ser comprado.",
	"El pedido está comprado y en proceso de llegar al almacén.",
	"El pedido se puede retirar del almacén por la unidad interesada.",
]

def get_depto(nombre_url):
	deptos = Departamento.objects.all()
	for d in deptos:
		depto = normalizar_url( str(d) )
		if depto == nombre_url:
			return d
	return None

def get_estado(nombre_url):
	estados = Estado.objects.all()
	for e in estados:
		estado = normalizar_url( str(e) )
		if estado == nombre_url:
			return e
	return None

def url_back(url, num):
	aux = url.split('/')
	tam = len(aux)-1
	new = '/'
	for x in range(1,tam-num):
		new += aux[x]+'/'
	return new

#devuelve el form si el estado se puede gestionar o si no se puede gestionar se devuelve None.
def get_form_gestion(id_estado, pedido):
	form = FormGestionar()
	form.fields['est_act'].queryset = choice_actual(pedido)
	form.fields['est_sig'].queryset = choice_siguiente(pedido)
	p_prods = pedido.producto_set.all()
	p_cots = pedido.cotizacion_set.all()
	if id_estado == 1: #No Publicado
		if p_prods:
			return form
	elif id_estado == 2: #Publicado
		for p in p_prods:
			if not p.renglon: return None
		return form
	elif id_estado == 3: #Con Presupuesto asignado
		return form
	elif id_estado == 4: #Aprobado por gerencia
		if not p_cots: return None
		for c in p_cots:
			prods = c.productoscotizados_set.all()
			for p in prods:
				if not p.precio: return None
			return form
	elif id_estado == 5: #Cotizado
		for c in p_cots:
			if not c.prioridad: return None
		return form
	elif id_estado == 6: #Con cotización ordenada
		for c in p_cots:
			if c.aprobada: return form
		return None
	elif id_estado in [7,8,9]: #Con cotización elegida, en almacén y retirado de almacén.
		return form
	return None



#Método para obtener un párrafo (p) y un formulario de gestión (form), para cuando se lista
#un pedido.
def get_p_y_form(nombre_estado, pedido):
	estado = get_estado(nombre_estado)
	estados = Estado.objects.all()
	for e in estados:
		if e == estado:
			return ps[e.id-1], get_form_gestion(e.id, pedido)

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
			ctx['url_redir'] = request.session['pedido_page']
			return render(request, 'GestionUser/info.html', ctx)

	ctx = {'titulo':'Error', 'titulo_msg':'No hay datos', 'url_redir':user.get_url_home()}
	return render(request, 'GestionUser/info.html', ctx)

class BaseSGPC(View):
	slug_url_kwarg = 'key'
	slug_field = 'id'
	model = Pedido
	pedido = None
	objeto_pedido = None #el modelo q pertenece a un pedido (Producto, Cotizacion, etc)
#Variable para crear, editar, etc un modelo cualquiera (Producto, Pedido, Cotizacion, etc)
	modelo = None
#para hacer comprobaciones a nivel de url
	comprobar_depto_url = True
	comprobar_estado_url = True
#para hacer comprobaciones del depto = a mi depto; y estado = mi estado gestion
	mi_depto = True #Asegura q el depto pasado por url me pertenece
	mi_gestion = False #Si es True, pregunta si el estado q se pasa por url, me pertenece para gestión
	filtrar_por_estado_url = True #devuelve sólo pedidos coincidentes con el estado (pasado por url)
	filtrar_por_mi_depto = True #Filtra pedidos solo pertencientes a mi depto
	modelo_no_publicado = False #para hacer la comprobación de si el modelo 'pk' es "No Publicado"
	estado_url = None #Obliga a pasar un estado por url igual al de ésta variable
	modelo_me_pertenece = True #Se usa para comprobar si el modelo pertence a mi depto
#para hacer comprobacion de si el estado de url es igual al estado del modelo pasado por 'pk'
	comprobar_estado_url_es_estado_model = False
#variable global q contendrá el error generado por alguna comprobación
	error = None
#variables de la clase
	depto = None #el depto pasado por url
	estado = None #el estado pasado por url
	estado_modelo = None #El estado del modelo (Pedido, Producto, Cotizacion, etc) "todos los q dependan del pedido"
	no_publicado = Estado.objects.get(id=1) #no publicado
	estado_gestion_user = None

	def __es_mi_depto(self, user): return self.depto == user.get_depto()
	def __es_mi_gestion(self, estado): return self.estado == estado
	def __model_estado(self, estado): return self.estado == estado
	def __es_no_publicado(self): return self.estado == self.estado_modelo

#comprueba si el nombre del depto pasado por url existe.
	def __comprobar_depto_url(self, depto_url):
		if self.comprobar_depto_url:
			self.depto = get_depto(depto_url)
			if not self.depto: 
				if not self.error: self.error = 'El departamento no existe.'
#comprueba que el nombre del estado pasado por url existe
	def __comprobar_estado_url(self, estado_url):
		if self.comprobar_estado_url:
			self.estado = get_estado(estado_url)
			if not self.estado:
				if not self.error: self.error = 'El estado no existe.'
#comprueba que el depto pasado por url sea el depto al q pertenezco.
	def __comprobar_si_el_depto_url_es_mi_depto(self, user):
		if self.mi_depto: #por defecto no se comprueba
			if self.depto: #si el depto pasado existe
				if self.depto != user.get_depto(): 
					if not self.error: self.error = 'No pertene al depto.'
#comprueba q el modelo pasado por 'pk' coincide con el estado pasado por url
	def __comprobar_estado_url_igual_a_estado_model(self, estado_model):
		if self.comprobar_estado_url_es_estado_model:
			if self.estado:
				if self.estado != estado_model:
					if not self.error: self.error = 'El estado del modelo no es "'+str(self.estado)+'".'
#comprueba q el estado pasado por url sea el estado q me toca gestionar
	def __comprobar_que_el_estado_url_sea_de_gestion(self, estado_gestion):
		print("ESTADO DE URL: " + str(self.estado))
		print("ESTADO DE GESTION: " + str(estado_gestion))
		if self.mi_gestion: #mi_gestion = False, desactiva la comprobación
			if self.estado:
				if self.estado != estado_gestion:
					if not self.error: self.error = 'No se puede gestionar el estado "'+str(self.estado)+'".'
#comprueba si el modelo pertenece al estado "No Publicado"
	def __modelo_es_no_publicado(self, estado_modelo):
		if estado_modelo and self.modelo_no_publicado:
			print("OK")
			if self.no_publicado != estado_modelo:
				if not self.error: self.error = 'El modelo es diferente al estado "'+str(self.no_publicado)+'".'
#comprueba si el modelo pertenece al mi depto
	def __modelo_pertenece_a_mi_depto(self, user):
		print("objeto_pedido")
		print(self.objeto_pedido)
		print(self.modelo_me_pertenece)
		if self.modelo_me_pertenece and self.objeto_pedido:
			print( str(self.objeto_pedido.usuario.get_depto()) +" != " +str(user.get_depto()) )
			if self.objeto_pedido.usuario.get_depto() != user.get_depto():
				print("NO PERTENECE")
				if not self.error: self.error = 'El modelo no pertenece al depto!'

#comprueba si el estado pasado por url es igual a la variable "estado_url"
	def __comprobar_estado_de_url(self):
		if self.estado_url:
			if self.estado_url != self.estado:
				if not self.error: self.error = 'El estado debe ser "'+str(self.estado_url)+'".'

	def __seg(self, user, estado_model):
		self.__comprobar_depto_url(self.kwargs['depto'])
		self.__comprobar_estado_url(self.kwargs['estado'])
		self.__comprobar_si_el_depto_url_es_mi_depto(user)
		self.__comprobar_estado_url_igual_a_estado_model(estado_model)
		self.__comprobar_que_el_estado_url_sea_de_gestion(self.estado_gestion_user)
		self.__comprobar_estado_de_url()
		objeto = None
		print("ERR: "+str(self.error) )
		if 'key' in self.kwargs and not self.error: #id de pedido
			try:
				objeto = Pedido.objects.get(id=self.kwargs['key'])
			except:
				if not self.error: self.error = 'Id del pedido no existe'
			print("KEY: "+str(objeto) )
			if 'id' in self.kwargs: #id de (Producto, Cotización)
				self.filtrar_por_mi_depto = False
				self.filtrar_por_estado_url = False
				try:
					objeto = self.modelo.objects.get(id=self.kwargs['id'])
				except:
					if not self.error: self.error = 'Id no existe'
				print("ID: "+str(objeto))
				if 'ki' in self.kwargs: #id de (ProductoCotizado, ComentarioCotizacion)
					try:
						objeto = self.modelo.objects.get(id=self.kwargs['ki'])
					except:
						if not self.error: self.error = 'Id no existe'
					print("KI: "+str(objeto))
			print("MODELO: " +str(self.objeto_pedido) )
			if isinstance(objeto, Pedido): #si es un pedido
				self.estado_modelo = objeto.estado
				self.objeto_pedido = objeto
			elif isinstance(objeto, Cotizacion) or isinstance(objeto, Producto):
				self.estado_modelo = objeto.pedido.estado
				self.objeto_pedido = objeto.pedido
			print("ESTADO OBJ: " +str(self.estado_modelo) )
		#Editar o Eliminar un modelo
			self.__modelo_es_no_publicado(self.estado_modelo)
			self.__modelo_pertenece_a_mi_depto(user)
		if self.modelo: 
			print("ASIGNANDO EL MODELO")
			self.model = self.modelo
		print("TODO OK")


	def get_queryset(self):
		#Para manejar una lista de objetos, según ciertos criterios
		queryset = self.model.objects.all() #todos los pedidos
		#retornar exactamente todos los pedidos en mi depto
		if self.filtrar_por_mi_depto:
			users = DeptoUser.objects.filter(depto=self.depto).values('usuario')
			queryset = queryset.filter(usuario=users)
		#retorna solo los pedidos filtrados por el estado pasado por url
		if self.filtrar_por_estado_url:
			queryset = queryset.filter(estado=self.estado)
		return queryset

	def solo_para_almacen(self, user):
		depto = Departamento.objects.get(id=16) #almacen
		estado_en_almacen = Estado.objects.get(id=9) #en_almacén
		estado_url = get_estado( str(self.kwargs['estado']) )
		if user.get_depto() == depto and estado_url == estado_en_almacen:
			self.estado_gestion_user = estado_en_almacen
			self.filtrar_por_mi_depto = False
		else:
			self.estado_gestion_user = user.get_estado()

	def dispatch(self, *args, **kwargs):
		url_back(self.request.path, 2)
		user = self.request.user
		estado_gestion = user.get_estado() #El estado q puedo gestionar
		self.solo_para_almacen(user)
		self.__seg(user, estado_gestion)
		if self.error:
			ctx = {'titulo':'Error', 'titulo_msg': self.error}
			return render(self.request, 'GestionUser/info.html', ctx)

		return super(BaseSGPC, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		print("EN EL CONTEXT")
		context = super(BaseSGPC, self).get_context_data(**kwargs)
		if self.estado:
			context['estado'] = self.estado.id
		return context

#Clase base para listar pedidos, uno por uno
class Listar(BaseSGPC, ListView):
	template_name = 'Genericas/list2.html'
	paginate_by = 1

	def dispatch(self, *args, **kwargs):
		url = self.request.path
		if 'page' in self.request.GET:
			url += '?page=' + self.request.GET['page']
		self.request.session['pedido_page'] = url
		return super(Listar, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Listar, self).get_context_data(**kwargs)
		print("LPG: objects_list: " +str(self.object_list))
		if self.object_list:
			p, form = get_p_y_form(self.kwargs['estado'], self.object_list[0])
			context['form_gestion'] = form
			context['parrafo'] = p
			context['h2'] = 'Pedido "'+ get_estado(self.kwargs['estado']).nombre +'"'
			context['form_renglon'] = FormRenglon()
			context['form_cotizar'] = FormProductoCotizado()
		return context

class Actualizar(BaseSGPC, UpdateView):
	template_name = 'Genericas/update.html'

class Crear(BaseSGPC, CreateView):
	template_name = 'Genericas/create.html'

class Eliminar(BaseSGPC, DeleteView):
	template_name = 'Genericas/delete.html'
	
#clase q lista todos los pedidos q pertenezcan a mi detpo y q pertenezan a estado
#pasado por url
class ListarDeptoEstado(Listar):
	filtrar_por_mi_depto = True
	filtrar_por_estado_url = True

#clase q lista los pedidos q puedo gestionar.
class ListarPedidosGestion(Listar):
	filtrar_por_mi_depto = False
	filtrar_por_estado_url = True
	mi_gestion = True #me asegura q el estado q pase por url, sea el q puedo gestionar.

#Clase para Crear un pedido nuevo
class CrearPedido(Crear):
	estado_url = Estado.objects.get(id=1)
	fields = ['justificacion', 'fecha']

	def form_valid(self, form):
		pedido = form.save(commit=False)
		pedido.usuario = self.request.user
		pedido.estado = Estado.objects.get(id=1)
		pedido.save()
		return redirect( url_back(self.request.path, 1) )

	def get_context_data(self, **kwargs):
		context = super(CrearPedido, self).get_context_data(**kwargs)
		context['h2'] = 'Nuevo Pedido'
		context['value_input'] = 'Crear Pedido'
		return context

#Clase para editar los pedidos "No Publicados"
class EditarPedido(Actualizar):
	model = Pedido
	fields = ['justificacion', 'fecha']
	modelo_no_publicado = True
	estado_url = Estado.objects.get(id=1)

	def get_success_url(self):
		return self.request.session['pedido_page']

	def get_context_data(self, **kwargs):
		context = super(EditarPedido, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Pedido'
		context['value_input'] = 'Guardar Cambios'
		return context

class EliminarPedido(Eliminar):
	slug_url_kwarg = 'key'
	slug_field = 'id'
	template_name = 'Genericas/delete.html'
	modelo = Pedido
	filtrar_por_estado_url = False
	filtrar_por_mi_depto = False
	modelo_no_publicado = True
	modelo_me_pertenece = True

	def get_success_url(self):
		return url_back(self.request.path, 2)

#Clase q crea un producto correspondiente a un pedido
class CrearProducto(Crear):
	template_name = 'Genericas/create.html'
	fields = ['descripcion', 'cantidad']
	modelo = Producto
	modelo_no_publicado = True
	modelo_me_pertenece = True

	def form_valid(self, form):
	 	producto = form.save(commit=False)
	 	producto.pedido = Pedido.objects.get(id=self.kwargs['key'])
	 	producto.save()
	 	return redirect( self.request.session['pedido_page'] )

	def get_context_data(self, **kwargs):
		context = super(CrearProducto, self).get_context_data(**kwargs)
		context['h2'] = 'Nuevo Producto'
		context['value_input'] = 'Crear Producto'
		return context

#Clase para editar los productos "No Publicados"
class EditarProducto(Actualizar):
	slug_url_kwarg = 'id'
	slug_field = 'id'
	modelo = Producto
	fields = ['descripcion', 'cantidad']
	modelo_no_publicado = True
	estado_url = Estado.objects.get(id=1)

	def get_success_url(self):
		return self.request.session['pedido_page']

	def get_context_data(self, **kwargs):
		context = super(EditarProducto, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Producto'
		context['value_input'] = 'Guardar Cambios'
		return context

class EditarRenglon(EditarProducto):
	fields = ['renglon']
	estado_url = Estado.objects.get(id=2)
	filtrar_por_mi_depto = False
	filtrar_por_estado_url = False

	def get_context_data(self, **kwargs):
		context = super(EditarProducto, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Renglón'
		context['value_input'] = 'Guardar Cambios'
		return context

#Clase q elimina un producto correspondiente a un pedido
class EliminarProducto(Eliminar):
	slug_url_kwarg = 'id'
	slug_field = 'id'
	modelo = Producto
	filtrar_por_mi_depto = False
	filtrar_por_estado_url = False

	def get_success_url(self):
		return url_back(self.request.path, 4)


# class AsignarRenglon(BaseSGPC, FormView):
# 	model = Producto
# 	fields = ['renglon']

# 	def form_valid(self, form):
# 	 	producto = form.save(commit=False)
# 	 	producto.pedido = Pedido.objects.get(id=self.request.POST['id'])
# 	 	producto.save()
# 	 	return redirect( self.request.session['pedido_page'] )

def asignarRenglon(request, depto, estado):
	if request.method == 'POST':
		id = request.POST['id']
		renglon = request.POST['renglon']
		if renglon == '':
			ctx = {"titulo":"Error", "titulo_msg":"Form no válido.", "url_redir":request.session['pedido_page']}
			return render(request, 'GestionUser/info.html', ctx)
		producto = Producto.objects.filter(id=id)
		producto.update(renglon=renglon)
	return redirect( request.session['pedido_page'] )

class CrearCotizacion(Crear):
	modelo = Cotizacion
	fields = ['proveedor', 'fecha_cotizacion', 'fecha_entrega']
	modelo_me_pertenece = False

	def form_valid(self, form):
	 	cotizacion = form.save(commit=False)
	 	pedido = Pedido.objects.get(id=self.kwargs['key'])
	 	productos = Producto.objects.filter(pedido=pedido)
	 	cotizacion.pedido = pedido
	 	cotizacion.save()
	 	for p in productos:
		 	ProductosCotizados.objects.create(
		 		producto = p,
		 		cantidad = p.cantidad,
		 		cotizacion = cotizacion
		 	)
	 	return redirect( self.request.session['pedido_page'] )

	def get_context_data(self, **kwargs):
		context = super(CrearCotizacion, self).get_context_data(**kwargs)
		context['h2'] = 'Nueva Cotización'
		context['value_input'] = 'Guardar Cotización'
		return context

	def get_success_url(self):
		return self.request.session['pedido_page']

class EditarCotizacion(Actualizar):
	slug_url_kwarg = 'id'
	slug_field = 'id'
	modelo = Cotizacion
	fields = ['proveedor', 'fecha_cotizacion', 'fecha_entrega']
	filtrar_por_estado_url = False
	filtrar_por_mi_depto = False

	def get_context_data(self, **kwargs):
		context = super(EditarCotizacion, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Cotización'
		context['value_input'] = 'Guardar Cambios'
		return context

	def get_success_url(self):
		return self.request.session['pedido_page']

class EliminarCotizacion(Eliminar):
	slug_url_kwarg = 'id'
	slug_field = 'id'
	modelo = Cotizacion
	filtrar_por_estado_url = False
	filtrar_por_mi_depto = False

	def get_success_url(self):
		return self.request.session['pedido_page']

def cotizarProducto(request, depto, estado):
	if request.method == 'POST':
		garantia = request.POST['garantia']
		precio = request.POST['precio']
		if precio == '' or garantia == '':
			ctx = {"titulo":"Error", "titulo_msg":"Form no válido.", "url_redir":request.session['pedido_page']}
			return render(request, 'GestionUser/info.html', ctx)
		id_producto = request.POST['id_producto']
		id_cotizacion = request.POST['id_cotizacion']
		producto = Producto.objects.get(id=id_producto)
		cantidad = producto.cantidad
		cotizacion = Cotizacion.objects.get(id=id_cotizacion)
		p = ProductosCotizados.objects.filter(
			producto = producto,
			cotizacion = cotizacion
		)
		p.update(
			garantia = garantia,
			precio = precio
		)
	return redirect( request.session['pedido_page'] )

class AsignarPrioridad(EditarCotizacion):
	fields = ['prioridad']

	def get_context_data(self, **kwargs):
		context = super(EditarCotizacion, self).get_context_data(**kwargs)
		context['h2'] = 'Asignar Prioridad'
		context['value_input'] = 'Guardar'
		return context

def seleccionarCotizacion(request, depto, estado, key, id):
	pedido = Pedido.objects.get(id=key)
	Cotizacion.objects.filter(pedido=pedido).update(aprobada=False)
	Cotizacion.objects.filter(id=id).update(aprobada=True)

	return redirect( request.session['pedido_page'] )

def verSeguimiento(request, depto):
	depto = get_depto(depto)
	users = DeptoUser.objects.filter(depto=depto).values('usuario')
	pedidos = Pedido.objects.filter(usuario=users)
	ctx = {'pedidos':pedidos}

	return render(request, 'Genericas/seguimiento.html', ctx)