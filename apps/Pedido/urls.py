from django.conf.urls import include, url, patterns
from .views import *

urlpatterns = patterns('',
    url(r'^ver/$', verPedidos),
    url(r'^nuevo/$', nuevoPedido),
    url(r'^producto/nuevo/$', nuevoProducto),
    url(r'^finalizar/$', finalizarPedido),
    url(r'^detalle/(?P<id>[-\w]+)/$', detallePedido),
    url(r'^editar/(?P<id>[-\w]+)/$', EditarProducto.as_view()),
    url(r'^gestionar/(?P<id>[-\w]+)/$', gestionarPedido),
    url(r'^no_publicado/$', ListaPedidosNoPublicados.as_view()),
    url(r'^en_almacen/$', ListaPedidosEnAlmacen.as_view()),
)