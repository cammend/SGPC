from django.conf.urls import include, url, patterns
from .views import (
	ListarDeptoEstado, ListarPedidosGestion, EditarPedido, EliminarPedido, CrearPedido,
	EditarProducto, CrearProducto, EliminarProducto, asignarRenglon, EditarRenglon,
	CrearCotizacion, EditarCotizacion, EliminarCotizacion,
	cotizarProducto, AsignarPrioridad, seleccionarCotizacion,
)

urlpatterns = patterns('',
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/$', ListarDeptoEstado.as_view()),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/$', ListarPedidosGestion.as_view()),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/asignar_renglon/$', asignarRenglon),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/editar_renglon/(?P<id>[-\w]+)/$', EditarRenglon.as_view()),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/agregar_cotizacion/(?P<key>[-\w]+)/$', CrearCotizacion.as_view()),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/editar_cotizacion/(?P<id>[-\w]+)/$', EditarCotizacion.as_view()),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/eliminar_cotizacion/(?P<id>[-\w]+)/$', EliminarCotizacion.as_view()),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/cotizar_producto/$', cotizarProducto),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/asignar_prioridad/(?P<id>[-\w]+)/$', AsignarPrioridad.as_view()),


	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/nuevo/$', CrearPedido.as_view()),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/(?P<key>[-\w]+)/editar_pedido/$', EditarPedido.as_view()),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/(?P<key>[-\w]+)/eliminar_pedido/$', EliminarPedido.as_view()),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/(?P<key>[-\w]+)/seleccionar/(?P<id>[-\w]+)/$', seleccionarCotizacion),

	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/(?P<key>[-\w]+)/agregar_producto/$', CrearProducto.as_view()),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/(?P<key>[-\w]+)/producto/(?P<id>[-\w]+)/editar/$', EditarProducto.as_view()),	
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/(?P<key>[-\w]+)/producto/(?P<id>[-\w]+)/eliminar/$', EliminarProducto.as_view()),

)