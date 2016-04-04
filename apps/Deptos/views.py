from django.shortcuts import render, redirect
from GestionUser.models import getDeptosUrl, getDeptos
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from .models import Departamento

# Create your views here.
def sgpc(request):
	return redirect('/sgpc/depto/home/')

@login_required
def home(request, depart):
	tipo = request.user.tipoUser
	if tipo == 0: #si es usuario ROOT
		return redirect('/sgpc/cuentas/nueva/')
	deptos_url = getDeptosUrl() #obtener la lista de las urls
	depto = request.user.depto
	if depart == 'home':
		return redirect('/sgpc/depto/'+str(deptos_url[depto]))
	ctx = {'depto':'d'}
	return render(request, 'Deptos/depto.html', ctx)

class NuevoDepto(CreateView):
	model = Departamento
	fields = '__all__'
	template_name = 'Deptos/nuevo_depto.html'