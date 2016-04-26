from django.shortcuts import render, redirect
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from apps.Pedido.models import Pedido, Producto
from apps.Estado.models import *

#Clase base que si se deriva de ella se asegura la seguridada a nivel de,
#Tipo de Usuario (ROOT, ADMIN, NORMAL)
#se requieren instanciar dos varibles obligatorias para usar ésta Clase
#Ejemplo:
#	model = Pedido
#	view  = CreateView
class Reciente():
	nombre = None
	url = None


def generar_recientes(lista, set_url):
	lista2 = None
	if lista:
		lista2 = []
		for l in lista:
			r = Reciente()
			r.nombre = l[0]
			if set_url:
				r.url = l[1]
			lista2.append(r)
	return lista2


"""
DESDE AQUI PARA ABAJO FUNCIONA TODO BIEN
"""

class BaseModeloView(View):
	#Éstas variables son las que dicen que tipo de usuario puede ver la vista
	user_root = False
	user_admin = True
	user_normal = True
	template_render = 'GestionUser/error.html'
	ctx = {'msg':'El usuario no puede ver ésta página'}
	nombre_actividad = None
	#Normalmente sólo los ADMIN y NORMAL pueden ver la vista
	@method_decorator(login_required)
	def dispatch(self, *args, **kwargs):
		print("BASE MODELO VIEW")
		if self.nombre_actividad:
			lista = self.request.session.get('reciente', [])
			aux = 0
			if lista:
				for l in lista:
					if self.nombre_actividad == l[0]:
						print(lista[aux])
						del lista[aux]
					aux += 1
				lista.append( [self.nombre_actividad, self.request.path] )
			else:
				lista.append( (self.nombre_actividad, self.request.path) )
			self.request.session['reciente'] = lista

		user = self.request.user
		if (user.es_root() and self.user_root) or (user.es_admin() and self.user_admin) or (user.es_normal() and self.user_normal):
			pass
		else:
			if self.request.path == user.get_url_home():
				print("URL HOME IGUAL Q PATH")
				return render(self.request, self.template_render, self.ctx)
			else:
				print("REDIRECT URL HOME")
				return redirect(user.get_url_home())
		print("NORMAL TODO")
		return super(BaseModeloView, self).dispatch(*args, **kwargs)


###############################################################
#Las siguientes clases derivan de "BaseModeloView" para tener seguridad a nivel de
#Tipo de Usuario (ROOT, ADMIN, NORMAL)
class BaseModeloListView(ListView, BaseModeloView):
	template_name = 'Genericas/list.html'

	def get_context_data(self, **kwargs):
		context = super(BaseModeloListView, self).get_context_data(**kwargs)
		lista = self.request.session.get('reciente', None)
		context['reciente'] = generar_recientes(lista, True)
		return context

class BaseModeloDetailView(DetailView, BaseModeloView):
	template_name = 'Genericas/detail.html'
	slug_url_kwarg = 'id'
	slug_field = 'id'

	def get_context_data(self, **kwargs):
		context = super(BaseModeloDetailView, self).get_context_data(**kwargs)
		lista = self.request.session.get('reciente', None)
		context['reciente'] = generar_recientes(lista, True)
		return context

class BaseModeloUpdateView(UpdateView, BaseModeloView):
	#Variables obligatorias del DetailView
	slug_url_kwarg = 'id'
	slug_field = 'id'
	template_name = 'Genericas/update.html'

	def get_context_data(self, **kwargs):
		context = super(BaseModeloUpdateView, self).get_context_data(**kwargs)
		lista = self.request.session.get('reciente', None)
		context['reciente'] = generar_recientes(lista, True)
		return context

class BaseModeloCreateView(CreateView, BaseModeloView):
	template_name = 'Genericas/create.html'

	def get_context_data(self, **kwargs):
		context = super(BaseModeloCreateView, self).get_context_data(**kwargs)
		lista = self.request.session.get('reciente', None)
		context['reciente'] = generar_recientes(lista, False)
		return context

class BaseModeloDeleteView(DeleteView, View):
	template_name = 'Genericas/delete.html'
	slug_url_kwarg = 'id'
	slug_field = 'id'

	def get_context_data(self, **kwargs):
		context = super(BaseModeloDeleteView, self).get_context_data(**kwargs)
		lista = self.request.session.get('reciente', None)
		context['reciente'] = generar_recientes(lista, False)
		return context

###############################################################


class algo(View):

	def dispatch(self, *args, **kwargs):
		print(self.request.path)
		return super(algo, self).dispatch(*args, **kwargs)

#Clase que deja pasar un pedido filtrando por "Estado"
class SeguridadPedidoEstado(algo):

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		id_pedido = None
		if 'id' in kwargs: id_pedido = kwargs['id']
		#Si es 0, seguimos sin comprobar
		if self.id_estado == 0: return super(SeguridadPedidoEstado, self).dispatch(*args, **kwargs)
		print("NO SEGURIDAD PEIDOD")
		#try:
		pedido = Pedido.objects.get(id=id_pedido) 
		estado = Estado.objects.get(id=self.id_estado)
		if pedido.estado == estado:
			return super(SeguridadPedidoEstado, self).dispatch(*args, **kwargs)
		#except:
		#	pass
		return render(self.request, 'GestionUser/info.html', self.ctx)

#Clase que deja pasar un producto filtrando por "Estado"
class SeguridadProductoEstado(View):
	ctx = None
	id_estado = 0

	#Acá se comprueba si el pedido al que pertenece éste producto, está en "No Publicado"
	def dispatch(self, *args, **kwargs):
		if self.id_estado is None:
			print("Se tiene q especificar un 'id_estado'")
		id_producto = kwargs['id']

		if self.id_estado != 0: return super(SeguridadProductoEstado, self).dispatch(*args, **kwargs)

		#Aca se comprueba si el pedido está en el estado elegido
		#try:
		pedido = Producto.objects.get(id=id_producto).pedido #Pedido al q pertenece el Producto
		estado = Estado.objects.get(id=self.id_estado)
		if pedido.estado == estado:
			print('ok')
			return super(SeguridadProductoEstado, self).dispatch(*args, **kwargs)
		#except:
		#	pass

		#Si se llega aquí... se muestra un ERROR
		self.success_url = recortar_url(self.request.path, 5)
		self.ctx = {'titulo':'Error', 'titulo_msg':'Pedido no encontrado'}
		estado = Estado.objects.get(id=self.id_estado)
		self.ctx['msg'] = 'Estado: "'+str(estado)+'".'
		self.ctx['url_redir'] = self.request.user.get_url_home()
		return render(self.request, 'GestionUser/info.html', self.ctx)
