from .models import Transicion, HistorialTrans

def get_historial_trans(user, pedido):
	return HistorialTrans.objects.filter(user=user,pedido=pedido)

def get_all_historia_pedido(pedido):
	return HistorialTrans.objects.filter(pedido=pedido)