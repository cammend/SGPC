from django.conf.urls import include, url, patterns
from .views import crearUsuario, eliminarUsuario, entrar, salir, index

urlpatterns = patterns('',
	url(r'^$', index),
    url(r'^nueva/$', crearUsuario),
    url(r'^eliminar/$', eliminarUsuario),
    url(r'^entrar/$', entrar),
    url(r'^salir/$', salir),
)