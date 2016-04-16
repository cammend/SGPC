from django.shortcuts import render
from .models import Estado, EstadoDepto
from apps.Deptos.models import Departamento
from apps.Deptos.forms import ListaDeptos
from .funciones import *

# Create your views here.

#Vista para asignar estados a un Depto
def addEstadoDepto(request):
	user = request.user
	form = ListaDeptos()
	ctx = {'form': form}
	if user.es_root():
		if request.method == 'POST':
			if 'id' in request.POST:
				idEst = request.POST['id']
				idDepto = request.POST['departamento']
				depto = get_depto_by_id(idDepto)
				estado = get_estado_by_id(idEst)
				if depto_has_estado(depto, estado):	del_depto_estado(depto, estado)
				else: add_depto_estado(depto, estado)
			if 'departamento' in request.POST:
				idDepto = request.POST['departamento']
				depto = Departamento.objects.filter(id=idDepto)
				est_asoc = get_estados_in_depto(depto)
				est_des = get_estados_out_depto(depto)
				form = ListaDeptos(data=request.POST)
				ctx['est_asoc'] = est_asoc
				ctx['est_des'] = est_des
				ctx['idDepto'] = idDepto
				ctx['form'] = form
		else:
			pass

	return render(request, 'Estado/estado_depto.html', ctx)

