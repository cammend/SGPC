from django.shortcuts import render
from apps.Pedido.view_based_class import *
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
# Create your views here.

#DeptoHome, muestra una lista de los pedidos para ser gestionados
class Home(BasePedidoListView):
	pedidos_para_gestionar = True
	#pedidos_no_publicados = False
	template_name = 'Deptos/depto.html'

#Listar todos los Deptos, solo para usuario root
class VerDeptos(BaseModeloListView):
	model = Departamento
	fields = ['nombre']
	template_name = 'Deptos/lista_deptos.html'
	user_root = True
	user_admin = False
	user_normal = False

#Crea un nuevo depto, solo para usuario root
class NuevoDepto(BaseModeloCreateView):
	model = Departamento
	fields = ['nombre']
	success_url = '/sgpc/depto/lista/'
	template_name = 'Deptos/nuevo_depto.html'
	user_root = True #la vista sólo la puede usar root
	user_admin = False
	user_normal = False