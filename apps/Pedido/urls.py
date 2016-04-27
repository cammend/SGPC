from django.conf.urls import include, url, patterns
from .views import *

urlpatterns = patterns('',
    #url(r'^producto/editar/(?P<id>[-\w]+)/$', EditarProducto.as_view()),
    url(r'^gestionar/$', gestionarPedido),
    url(r'^gestionar/(?P<id>[-\w]+)/$', DetallePedidoGestionar.as_view()),
    url(r'^gestionar/(?P<id>[-\w]+)/guardar_renglon/$', guardarRenglon),

    url(r'^gestionar/(?P<id>[-\w]+)/cotizar/$', guardarCotizacion),
    url(r'^gestionar/cotizacion/(?P<id>[-\w]+)/$', EditarCotizacion.as_view()),
    url(r'^gestionar/cotizacion/(?P<id>[-\w]+)/pedido/$', guardarProductosCotizados),
    url(r'^gestionar/cotizacion/(?P<id>[-\w]+)/eliminar/$', EliminarCotizacion.as_view()),

    url(r'^nuevo/$', CrearPedidoNoPublicado.as_view()), #Nuevo Pedido
    url(r'^no_publicado/$', ListarPedidosNoPublicados.as_view()), #Listar pedidos
    url(r'^no_publicado/(?P<id>[-\w]+)/$', DetallePedidoNoPublicado.as_view()), #Detalle pedido
    url(r'^no_publicado/(?P<id>[-\w]+)/editar/$', EditarPedidoNoPublicado.as_view()), #Editar pedido
    url(r'^no_publicado/(?P<id>[-\w]+)/eliminar/$', EliminarPedidoNoPublicado.as_view()), #Eliminar

    url(r'^no_publicado/(?P<id>[-\w]+)/producto/agregar/$', NuevoProducto.as_view()), #Nuevo Producto
    url(r'^no_publicado/([0-9]+)/producto/(?P<id>[-\w]+)/eliminar/$', EliminarProductoNoPublicado.as_view()), #Eliminar producto
    url(r'^no_publicado/([0-9]+)/producto/(?P<id>[-\w]+)/editar/$', EditarProductoNoPublicado.as_view()), #Editar producto

    url(r'^listar/$', ListarTodosLosPedidos.as_view()),
    url(r'^detalle/(?P<id>[-\w]+)/$', DetalleDePedido.as_view()),

    url(r'^gestionar/cotizaciones/(?P<id>[-\w]+)/$', AsignarPrioridadCot.as_view()),
    url(r'^para_comprar/$', ListarPedidosParaComprar.as_view()),
    url(r'^para_comprar/(?P<id>[-\w]+)/$', DetallePedidoParaComprar.as_view()),
)