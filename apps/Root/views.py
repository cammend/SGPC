from django.shortcuts import render
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic import TemplateView
from GestionUser.models import Departamento
from django.contrib.auth.decorators import login_required
from apps.Estado.models import Estado
from apps.Transicion.models import Transicion
from apps.Cotizacion.models import Prioridad

#Clase para requerir logueo.
class RequiereLogin(object):
	@classmethod
	def as_view(cls, **initkwargs):
		vista = super(RequiereLogin, cls).as_view(**initkwargs)
		return login_required(vista)

class SegTipoUser(object):
	user_root = False
	user_admin = False
	user_normal = False
	user = None

	def es_root(self): return self.user_root and self.user.es_root()
	def es_admin(self): return self.user_admin and self.user.es_admin()
	def es_normal(self): return self.user_normal and self.user.es_normal()

	def dispatch(self, *args, **kwargs):
		self.user = self.request.user

		if self.es_root() or self.es_admin() or self.es_normal():
			return super(SegTipoUser, self).dispatch(*args, **kwargs)

		ctx = {'titulo': 'Error', 'titulo_msg': 'Página no encontrada'}
		return render(self.request, 'GestionUser/info.html', ctx)


# Create your views here.

#Clases genéricas con seguridad!!!
class Listar(RequiereLogin, SegTipoUser, ListView):
	user_root = True #solo usuario root pueden acceder

class Crear(RequiereLogin, SegTipoUser, CreateView):
	user_root = True #solo usuario root pueden acceder

class Actualizar(RequiereLogin, SegTipoUser, UpdateView):
	user_root = True #solo usuario root pueden acceder
	slug_url_kwarg = 'id'
	slug_field = 'id'

class Eliminar(RequiereLogin, SegTipoUser, DeleteView):
	user_root = True #solo usuario root pueden acceder

class Detalle(RequiereLogin, SegTipoUser, DetailView):
	user_root = True #solo usuario root pueden acceder

class Plantilla(RequiereLogin, SegTipoUser, TemplateView):
	user_root = True #solo usuario root pueden acceder

def root(request):
	return render(request, 'Root/root.html')

#Mis vistas basadas en clase!!!
class Root(Plantilla):
	template_name = 'Root/root.html'


class ListarDeptos(Listar):
	template_name = 'Root/list.html'
	model = Departamento

class NuevoDepto(Crear):
	model = Departamento
	template_name = 'Root/create.html'
	fields = ['nombre']
	success_url = '/sgpc/root/lista_deptos/'

	def get_context_data(self, **kwargs):
		context = super(NuevoDepto, self).get_context_data(**kwargs)
		context['h2'] = 'Nuevo Departamento'
		return context

class EditarDepto(Actualizar):
	template_name = 'Root/update.html'
	model = Departamento
	fields = ['nombre']
	success_url = '/sgpc/root/lista_deptos/'

	def get_context_data(self, **kwargs):
		context = super(EditarDepto, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Nombre'
		return context

class EliminarDepto(Eliminar):
	pass

class ListarEstados(Listar):
	template_name = 'Estado/list.html'
	model = Estado

class DetalleEstado(Actualizar):
	template_name = 'Estado/update.html'
	model = Estado
	fields = ['nombre']
	success_url = '/sgpc/root/lista_estados/'

	def get_context_data(self, **kwargs):
		context = super(DetalleEstado, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Nombre'
		return context

class NuevoEstado(Crear):
	template_name = 'Estado/update.html'
	model = Estado
	fields = ['nombre']
	success_url = '/sgpc/root/lista_estados/'

	def get_context_data(self, **kwargs):
		context = super(NuevoEstado, self).get_context_data(**kwargs)
		context['h2'] = 'Nuevo Estado'
		return context

class ListarTransiciones(Listar):
	template_name = 'Transicion/list.html'
	model = Transicion

class NuevaTransicion(Crear):
	template_name = 'Transicion/create.html'
	model = Transicion
	fields = '__all__'
	success_url = '/sgpc/root/lista_transiciones/'

	def get_context_data(self, **kwargs):
		context = super(NuevaTransicion, self).get_context_data(**kwargs)
		context['h2'] = 'Nueva Transición'
		return context

class DetalleTransicion(Actualizar):
	template_name = 'Estado/update.html'
	model = Transicion
	fields = '__all__'
	success_url = '/sgpc/root/lista_transiciones/'

	def get_context_data(self, **kwargs):
		context = super(DetalleTransicion, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Transicion'
		return context

class ListarPrioridades(Listar):
	template_name = 'Prioridad/list.html'
	model = Prioridad

class NuevaPrioridad(Crear):
	template_name = 'Prioridad/create.html'
	model = Prioridad
	fields = '__all__'
	success_url = '/sgpc/root/lista_prioriades/'

	def get_context_data(self, **kwargs):
		context = super(NuevaPrioridad, self).get_context_data(**kwargs)
		context['h2'] = 'Nueva Transición'
		return context

class DetallePrioridad(Actualizar):
	template_name = 'Prioridad/update.html'
	model = Prioridad
	fields = '__all__'
	success_url = '/sgpc/root/lista_prioriades/'

	def get_context_data(self, **kwargs):
		context = super(DetallePrioridad, self).get_context_data(**kwargs)
		context['h2'] = 'Editar Prioridad'
		return context