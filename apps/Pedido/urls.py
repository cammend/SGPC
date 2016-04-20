from django.conf.urls import include, url, patterns
from .views import verPedidos, DetallePedido, nuevoPedido, nuevoProducto, finalizarPedido, detallePedido, EditarProducto, gestionarPedido

urlpatterns = patterns('',
    url(r'^ver/$', verPedidos),
    url(r'^detalle/(?P<id>[-\w]+)/$', DetallePedido.as_view()),
    url(r'^nuevo/$', nuevoPedido),
    url(r'^producto/nuevo/$', nuevoProducto),
    url(r'^finalizar/$', finalizarPedido),
    url(r'^detalle/(?P<id>[-\w]+)/$', detallePedido),
    url(r'^editar/(?P<id>[-\w]+)/$', EditarProducto.as_view()),
    url(r'^gestionar/(?P<id>[-\w]+)/$', gestionarPedido),
)