from django.conf.urls import include, url, patterns
from .views import home, NuevoDepto
from apps.Estado.views import addEstadoDepto
from apps.Pedido.views import verPedidos, DetallePedido

urlpatterns = patterns('',
    url(r'^home/$', home),
    url(r'^nuevo/$', NuevoDepto.as_view()),
    url(r'^pedidos/$', verPedidos),
    url(r'^$', addEstadoDepto),
    url(r'^detalle/(?P<id>[-\w]+)/$', DetallePedido.as_view()),
)