from django.conf.urls import include, url, patterns
from .views import ListarDeptoEstado, ListarEstado

urlpatterns = patterns('',
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/$', ListarDeptoEstado.as_view()),
	url(r'^(?P<depto>[-\w]+)/pedido/(?P<estado>[-\w]+)/gestion/$', ListarEstado.as_view()),
)