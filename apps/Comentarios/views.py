from django.shortcuts import render, redirect
from .forms import FormComentarioPedido, FormComentarioCot
from apps.Pedido.models import Pedido
from apps.Cotizacion.models import Cotizacion

# Create your views here.
def ComentarioPedido(request, depto):
	form = FormComentarioPedido()
	ctx = {'form_pedido': form}
	if request.method == 'POST':
		form = FormComentarioPedido(request.POST)
		id = request.POST['id']
		pedido = Pedido.objects.get(id=id)
		if form.is_valid():
			form.save(request.user, pedido)
			return redirect(request.session['pedido_page'])
		else:
			ctx['form_pedido'] = form
	return render(request, 'GestionUser/info.html')

def ComentarioCot(request, depto):
	form = FormComentarioCot()
	ctx = {'form_pedido': form}
	if request.method == 'POST':
		form = FormComentarioCot(request.POST)
		id = request.POST['id']
		cotizacion = Cotizacion.objects.get(id=id)
		if form.is_valid():
			form.save(request.user, cotizacion)
			return redirect(request.session['pedido_page'])
		else:
			ctx['form_pedido'] = form
	return render(request, 'GestionUser/info.html')