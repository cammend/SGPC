from django.shortcuts import render
from django.views.generic.list import ListView
from apps.Pedido.models import Pedido
from apps.Deptos.models import Departamento
from apps.Estado.models import Estado, EstadoDepto
from GestionUser.models import DeptoUser

# Create your views here.

deptos = [
		'presupuesto',
		'gerencia',
		'compras',
		'deptos_tecnicos',
		'finanzas',
		'almacen',
		'recursos_humanos',
]

def get_depto(nombre_url):
	if nombre_url == deptos[0]:   return Departamento.objects.get(id=11)
	elif nombre_url == deptos[1]: return Departamento.objects.get(id=12)
	elif nombre_url == deptos[2]: return Departamento.objects.get(id=13)
	elif nombre_url == deptos[3]: return Departamento.objects.get(id=14)
	elif nombre_url == deptos[4]: return Departamento.objects.get(id=15)
	elif nombre_url == deptos[5]: return Departamento.objects.get(id=16)
	elif nombre_url == deptos[6]: return Departamento.objects.get(id=17)
	return None

estados = [
	'no_publicado',
	'publicado',
	'presupuesto_asignado',
	'aprobado_gerente',
	'cotizado',
	'cotizacion_ordenada',
	'cotizacion_elegida',
	'comprado',
	'en_almacen',
	'retirado_almacen',
	'cancelado',
]

def get_estado(nombre_url):
	if nombre_url == estados[0]:   return Estado.objects.get(id=1)
	elif nombre_url == estados[1]: return Estado.objects.get(id=2)
	elif nombre_url == estados[2]: return Estado.objects.get(id=3)
	elif nombre_url == estados[3]: return Estado.objects.get(id=4)
	elif nombre_url == estados[4]: return Estado.objects.get(id=5)
	elif nombre_url == estados[5]: return Estado.objects.get(id=6)
	elif nombre_url == estados[6]: return Estado.objects.get(id=7)
	elif nombre_url == estados[7]: return Estado.objects.get(id=8)
	elif nombre_url == estados[8]: return Estado.objects.get(id=9)
	elif nombre_url == estados[9]: return Estado.objects.get(id=10)
	elif nombre_url == estados[10]:return Estado.objects.get(id=11)
	return None

def normalizar_depto(nombre):
	return nombre.lower().replace(' ','_').replace('.','')

class Listar(ListView):
	template_name = 'Genericas/list2.html'
	paginate_by = 1
	model = Pedido
	error = None
	depto = None
	estado = None
	mi_depto = False #Asegura q el depto pasado por url me pertenece
	mi_gestion = False #Si es True, pregunta si el estado q se pasa por url, me pertenece para gestión

	def __seg(self, user, estado):
		self.depto = get_depto(self.kwargs['depto'])
		self.estado = get_estado(self.kwargs['estado'])
		if not self.depto and not self.estado:	
			self.error = 'Página no encontrada.'
		elif self.depto != user.get_depto() and self.mi_depto:
			self.error = 'No pertenece al depto.'
		elif (self.estado != estado) and self.mi_gestion:
			self.error = 'Pedido no disponible para gestión.'

		print("Est. URL: "+str(self.estado) + str(self.estado.id))
		print("Est. Mio: "+str(estado) + str(estado.id))

	def get_queryset(self):
		if self.depto and not self.mi_gestion and self.estado:
			users = DeptoUser.objects.filter(depto=self.depto).values('usuario')
			return Pedido.objects.filter(usuario=users, estado=self.estado)
		elif self.estado: return Pedido.objects.filter(estado=self.estado)
		return Pedido.objects.all()

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		estado = user.get_estado()
		self.__seg(self.request.user, estado)
		if self.error:
			ctx = {'titulo':'Error', 'titulo_msg': self.error}
			return render(self.request, 'GestionUser/info.html', ctx)

		return super(Listar, self).dispatch(*args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super(Listar, self).get_context_data(**kwargs)
		context['estado'] = self.estado.id
		return context

class ListarDeptoEstado(Listar):
	mi_depto = True

class ListarEstado(Listar):
	mi_gestion = True