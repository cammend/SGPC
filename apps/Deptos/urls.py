from django.conf.urls import include, url, patterns
from .views import home, NuevoDepto
from apps.Pedido.views import verPedidos, DetallePedido, nuevoPedido, nuevoProducto, finalizarPedido, detallePedido

urlpatterns = patterns('',
    url(r'^home/$', home),
    url(r'^nuevo/$', NuevoDepto.as_view()),
    url(r'^pedido/ver/$', verPedidos),
    url(r'^detalle/(?P<id>[-\w]+)/$', DetallePedido.as_view()),
    url(r'^pedido/nuevo/$', nuevoPedido),
    url(r'^producto/nuevo/$', nuevoProducto),
    url(r'^pedido/finalizar/$', finalizarPedido),
    url(r'^pedido/detalle/(?P<id>[-\w]+)/$', detallePedido),

)