from django.conf.urls import include, url, patterns
from .views import (
	ListarDeptos, NuevoDepto, EditarDepto, Root, 
	ListarEstados, DetalleEstado, NuevoEstado,
	ListarTransiciones, NuevaTransicion, DetalleTransicion,
	ListarPrioridades, NuevaPrioridad, DetallePrioridad,
)
from apps.Estado.views import addEstadoDepto

urlpatterns = patterns('',
	url(r'^$', Root.as_view()),
	url(r'^lista_deptos/$', ListarDeptos.as_view()),
	url(r'^nuevo_depto/$', NuevoDepto.as_view()),
	url(r'^depto/(?P<id>[-\w]+)/$', EditarDepto.as_view()),
	url(r'^asociar/$', addEstadoDepto),

	url(r'^lista_estados/$', ListarEstados.as_view()),
	url(r'^nuevo_estado/$', NuevoEstado.as_view()),
	url(r'^estado/(?P<id>[-\w]+)/$', DetalleEstado.as_view()),

	url(r'^lista_transiciones/$', ListarTransiciones.as_view()),
	url(r'^nueva_transicion/$', NuevaTransicion.as_view()),
	url(r'^transicion/(?P<id>[-\w]+)/$', DetalleTransicion.as_view()),

	url(r'^lista_prioridades/$', ListarPrioridades.as_view()),
	url(r'^nueva_prioridad/$', NuevaPrioridad.as_view()),
	url(r'^prioridad/(?P<id>[-\w]+)/$', DetallePrioridad.as_view()),
)