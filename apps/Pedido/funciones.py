from .models import Pedido, Producto
from apps.Estado.models import Estado, EstadoDepto
from apps.Cotizacion.models import Cotizacion, ProductosCotizados
from django.db.models import Sum, F, Avg, FloatField, ExpressionWrapper
from apps.Deptos.funciones import *
from GestionUser.funciones import *
from GestionUser.models import Departamento
from .forms import *

NO_PUBLICADO = 1
COTIZACION_ORD = 6
RETIRADO_ALMACEN = 10

def get_choice_for_cot(cot):
	pedido = cot.pedido
	#Obtenemos todos los productos q se pueden cotizar
	productos = Producto.objects.filter(pedido=pedido)
	#Convertir a una lista el QuerySet
	productos = list(productos)

	#Eliminamos de la lista los productos ya cotizados
	aux = 0
	for p in productos:
		try:
			prod = ProductosCotizados.objects.get(producto=p, cotizacion=cot)
			if prod:
				del productos[aux]
			aux += 1
		except:
			pass

	#Creamos la lista
	lista = [ ('', 'Elija Opción') ]
	for p in productos:
		lista.append( (p.id,p.descripcion) )
	return lista

def get_form_for_depto(depto):
	__depto = Departamento.objects.all()
	if depto == __depto[0]: #PRESUPUESTO
		form = FormAsignaRenglon()
		form.fields['renglon'].label = ''
		return form
	return None

def get_template_for_depto(depto):
	__depto = Departamento.objects.all()

	if depto == __depto[0]: #PRESUPUESTO
		return 'Pedido/pedido_presupuesto.html'
	elif depto == __depto[1]: #GERENCIA
		return 'Pedido/pedido_gerencia.html'
	elif depto == __depto[2]: #COMPRAS
		return 'Pedido/pedido_compras.html'
	elif depto == __depto[3]: #DEPTOS TECNICOS
		return 'Pedido/pedido_deptos.html'
	return 'Pedido/detalle_pedido.html'

def pedido_se_puede_gestionar(pedido):
	#Variables
	estados = Estado.objects.all()
	estado_pedido = pedido.estado
	print(estados[0])
	print(estado_pedido)

#Un pedido "No Publicado" se puede "Publicar" sólo si tiene algún "Producto creado"
	if estado_pedido == estados[0]: #NO PUBLICADO
		p = Producto.objects.filter(pedido=pedido)
		if p: return True

#Un pedido "Publicado" pasa a gerencia, sólo si se le asignó el "renglón presupuestario"
#a cada producto del pedido
	#Empieza en 1, ya q el 0 es "No Publicado"
	elif estado_pedido == estados[1]: #PUBLICADO
		prods = Producto.objects.filter(pedido=pedido)
		for p in prods:
			if p.renglon is None:
				return False
		return True

	elif estado_pedido == estados[2]: #CON PRESUPUESTO ASIGNADO
		return True
	elif estado_pedido == estados[3]: #APROBADO POR GERENTE
		cotizaciones = Cotizacion.objects.filter(pedido=pedido)
		print(cotizaciones)
		for c in cotizaciones:
			productos = ProductosCotizados.objects.filter(cotizacion=c)
			print(productos)
			if not productos:
				return False
		return True

#Solo si todas las cotizaciones están con alguna prioridad asignada
	elif estado_pedido == estados[4]: #COTIZADO
		cotizaciones = Cotizacion.objects.filter(pedido=pedido)
		for c in cotizaciones:
			if c.prioridad is None:
				return False
		return True

	elif estado_pedido == estados[5]: #CON COTIZACIONES ORDENADAS
		pass
	elif estado_pedido == estados[6]: #CON COTIZACION ELEGIDA
		pass
	elif estado_pedido == estados[7]: #COMPRADO
		pass
	elif estado_pedido == estados[8]: #EN ALMACEN
		pass
	elif estado_pedido == estados[9]: #RETIRADO DE ALMACEN
		pass
	elif estado_pedido == estados[10]: #CANCELADO
		pass
	return False

def make_choices_from_tran(query):
	choices = [('','Elija Opción')]
	for q in query:
		item = (q.estadoSiguiente.id, q.estadoSiguiente.nombre)
		choices.append(item)
	return choices


#True si el pedido está en mi depto
def pedido_en_mi_depto(user, id_pedido):
	depto_u = user.get_depto()
	depto_p = None
	try:
		depto_p = Pedido.objects.get(id=id_pedido).usuario.get_depto()
		if depto_u == depto_p:
			return True
	except:
		pass
	return False

def pedido_para_gestionar(user, id_pedido):
	depto_u = user.get_depto()
	try:
		e_d = EstadoDepto.objects.filter(depto=depto_u)
		pedido = Pedido.objects.get(id=id_pedido)
		for e in e_d:
			if e.estado == pedido.estado:
				return True
	except:
		pass
	return False

#Devuelve true si el pedido no está publicado
def pedido_no_publicado(user, id_pedido):
	try:
		estado = Estado.objects.get(id=1)
		pedido = Pedido.objects.get(id=id_pedido)
		if estado == pedido.estado:
			return True
	except:
		pass
	return False

def recortar_url(url, num_dejar):
	url_n = url.split('/')
	nueva_url = ''
	num = 0
	for u in url_n:
		nueva_url = nueva_url+u+'/'
		if num == num_dejar:
			return nueva_url
		num += 1


#### ETIQUETA QUE SE USA PARA GUARDAR EL PEDIDO EN LA SESION
PEDIDO_EN_SESION = 'pedido_en_sesion'


#Retorna un identificador para obtener el pedido, si el pedido pertenece al usuario!
def si_es_mi_pedido_guardar(request, user, pedido):
	if pedido.usuario == user:
		request.session[PEDIDO_EN_SESION] = pedido.id
		return PEDIDO_EN_SESION
	return None

#Retorna un identificador para obtener el pedido, si el pedido pertenece al depto del usuario!
def si_pedido_en_mi_depto_guardar(request, user, pedido):
	depto_u = get_depto_of_user(user)
	depto_p = get_depto_of_pedido(pedido)
	if depto_p == depto_u:
		request.session[PEDIDO_EN_SESION] = pedido.id
		return PEDIDO_EN_SESION
	return None

#Retornar todos los pedidos no publicados
def get_all_pedidos_no_publicados(user):
	users = get_all_user_of_depto(user)
	no_public = Estado.objects.filter(id=1) #Estado no publicado
	try:
		lista = Pedido.objects.filter(usuario=users, estado=no_public)
		return lista
	except:
		pass
	return None

#Obtenemos el pedido guardado en sesión y lo eliminamos de la misma
def get_pedido_sesion_y_eliminar(request):
	if PEDIDO_EN_SESION in request.session:
		return request.session.pop(PEDIDO_EN_SESION)
	return None

#Obtenemos el pedido guardado en sesion sin eliminarlo
def get_pedido_sesion(request):
	if PEDIDO_EN_SESION in request.session:
		return request.session[PEDIDO_EN_SESION]
	return None

#Método para obtener todos los pedidos hechos por un usuario
def get_all_pedidos_by_user(user):
	return Pedido.objects.filter(usuario=user)

#Método para obtener todos los productos de un pedido
def get_all_producto_of_pedido(pedido):
	return Producto.objects.filter(pedido=pedido)

#Método para obtener todos los pedidos pertenecientes a un Depto
def get_all_pedidos_by_depto(user):
	lista_u = get_all_user_by_depto(user)
	lista_p = []
	for u in lista_u:
		lista = Pedido.objects.filter(usuario=u.usuario)
		for p in lista:
			lista_p.append(p)
	return lista_p
	#Retorna una Lista

#Método que retorna todos los pedidos gestionados en el Depto del usuario logueado
def get_all_gestion_by_depto(user):
	q_lista_users = get_all_user_by_depto(user)
	q_lista_pedido = Pedido.objects.filter(usuario=q_lista_users)
	for p in q_lista_pedido:
		q_lista_pedido.appendlist( 'trans',get_all_historial_pedido(p) )
	return q_lista_pedido

def get_all_productos_by_depto(user):
	lista_p = get_all_pedidos_by_depto(user)
	for p in lista_p:
		pass	

def get_depto_of_pedido(pedido):
	user = pedido.usuario
	return get_depto_of_user(user)

#Método para generar una lista de ids de alguna lista de Modelos
def generate_list_of_id(list_model):
	lista_ids = []
	for l in list_model:
		lista_ids.append(l.id)
	return lista_ids

#Pasando un id de un modelo, me devuelve el id de la list_model
def get_index_of_list_model(id, list_model):
	aux = 0
	for l in list_model:
		if (l.id == id): return aux
		else: aux += 1
	return None

def get_next_of_list_model(id, list_model):
	enviar = False
	for l in list_model:
		if enviar: return l
		if (int(l) == int(id)): enviar = True
	return None

def get_back_of_list_model(id, list_model):
	aux = None
	primero = True
	for l in list_model:
		if (int(l) == int(id)): return aux
		if primero:	primero = False
		else: aux = l
	return None


def pedido_tiene_productos(id_pedido):
	pedido = Pedido.objects.get(id=id_pedido)
	try:
		productos = Producto.objects.filter(pedido=pedido)
		if productos:
			return True
	except:
		pass
	return False

#Devuelve True si el pedido va para cualquier Depto, o sea q va para las unidades interesadas
#Es True sólo si tiene los estados "No Aprobado" o "Contizacion Ordenada"
def es_pedido_ordinario(id_pedido):
	pedido = Pedido.objects.get(id=id_pedido)
	est_p = pedido.estado
	est_no_apr = Estado.objects.get(id=1) #No Aprobado
	est_cot_ord = Estado.objects.get(id=6) #Cotización Ordenada
	if (est_p == est_no_apr) or (est_p == est_cot_ord):
		return True
	return False


#Se retorna un diccionario con todos los datos del pedido:
#PEDIDO (estado: con contizacion elegida)
#--COTIZACION (elegida)
#----PRODUCTOS (cotizados)
def __pedido_cot_prod(id_pedido):
	ctx = {}
	pedido = Pedido.objects.get(id=id_pedido)
	cotizacion = None
	try:
		cotizacion = Cotizacion.objects.get(pedido=pedido, aprobada=True)
	except:
		ctx['error'] = 'Éste pedido no tiene una cotización aprobada!'
		return ctx
	
	productos  = ProductosCotizados.objects.filter(cotizacion=cotizacion)
	products = productos.annotate( total=ExpressionWrapper( F('cantidad')*F('precio'), output_field=FloatField() ) )
	total = products.aggregate(Sum(F('total')))
	print(products)
	ctx['pedido'] = pedido
	ctx['cotizacion'] = cotizacion
	ctx['productos'] = products
	ctx['total'] = total['total__sum'] 
	return ctx

def __pedido_prod(id_pedido):
	ctx = {}
	pedido = Pedido.objects.get(id=id_pedido)
	productos  = Producto.objects.filter(pedido=pedido)
	products = productos.annotate( total=ExpressionWrapper( F('cantidad')*F('precio'), output_field=FloatField() ) )
	total = products.aggregate(Sum(F('total')))
	print(products)
	ctx['pedido'] = pedido
	ctx['productos'] = products
	ctx['total'] = total['total__sum']
	return ctx


#Cambia el estado de un pedido
def __cambiar_estado_pedido(id_pedido, id_estado):
	estado = Estado.objects.get(id=id_estado)
	Pedido.objects.filter(id=id_pedido).update(estado=estado)


################################################################ UNIDAD INTERESADA
def gestion_unidad_interesada(id_pedido):
	pass

#Cuando se gestiona un 'No Publicado' solo pasa a 'Publicado'
def gestionar_unidad_interesada(user, id_pedido, id_estado):
	__cambiar_estado_pedido(id_pedido, id_estado)
	ctx = {}
	ctx['titulo'] = 'Gestionado'
	ctx['titulo_msg'] = 'Pedido Publicado'
	ctx['url_redir'] = '/sgpc/depto/pedido/no_publicado/'
	return ctx
#***************************************************************

################################################################ PRESUPUESTO
def gestion_presupuesto(id_pedido):
	ctx = __pedido_prod(id_pedido)
	ctx['id_est_renglon'] = 3
	return ctx

def gestionar_presupuesto(user, id_pedido, id_estado):
	__cambiar_estado_pedido(id_pedido, id_estado)
	ctx = {}
	ctx['titulo'] = 'Gestionado'
	ctx['titulo_msg'] = 'Renglon Asignado'
	ctx['url_redir'] = user.get_url_home()
	return ctx
#***************************************************************

################################################################ GERENCIA
def gestion_gerencia(id_pedido):
	ctx = __pedido_prod(id_pedido)
	ctx['id_est_aprobado'] = 4
	ctx['id_est_cancelado'] = 11

def gestionar_gerencia(user, id_pedido, id_estado):
	__cambiar_estado_pedido(id_pedido, id_estado)
	titulo_msg = ''
	if id_estado == 4: titulo_msg = 'Pedido Aprobado'
	else: titulo_msg = 'Pedido Cancelado'
	ctx = {}
	ctx['titulo'] = 'Gestionado'
	ctx['titulo_msg'] = titulo_msg
	ctx['url_redir'] = user.get_url_home()
	return ctx
#***************************************************************

################################################################ FINANZAS
def gestion_finanzas(id_pedido):
	ctx = __pedido_cot_prod(id_pedido)
	ctx['id_est_comprado'] = 8 #Estado 'Comprado'
	return ctx

#Cuando se compra una cotización elegida se debe cambiar de estado al pedido (comprado)
def gestionar_finanzas(user, id_pedido, id_estado):
	__cambiar_estado_pedido(id_pedido, id_estado)
	ctx = {}
	ctx['titulo'] = 'Gestionado'
	ctx['titulo_msg'] = 'Pedido Comprado'
	ctx['url_redir'] = user.get_url_home()
	return ctx
#***************************************************************

def gestionar_almacen(user, id_pedido, id_estado):
	__cambiar_estado_pedido(id_pedido, id_estado)
	ctx = {}
	ctx['titulo'] = 'Gestionado'
	ctx['titulo_msg'] = 'Pedido Publicado'
	ctx['url_redir'] = '/sgpc/depto/pedido/no_publicado/'
	return ctx