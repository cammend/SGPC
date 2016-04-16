from django.shortcuts import render
from .funciones import *
from django.views.generic.detail import DetailView
from .models import Pedido, Producto

# Create your views here.
def verPedidos(request):
	user = request.user
	lista = get_all_pedidos_by_depto(user)
	ctx = {'lista': lista}
	return render(request, 'probar_listas.html', ctx)

class DetallePedido(DetailView):
	model = Pedido
	template_name = 'probar_listas.html'
	slug_url_kwarg = 'id'
	slug_field = 'id'