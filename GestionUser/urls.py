from django.conf.urls import include, url, patterns
from .views import crearUsuario, eliminarUsuarioView, entrar, salir

urlpatterns = patterns('',
    url(r'^nueva/$', crearUsuario),
    url(r'^eliminar/$', eliminarUsuarioView),
    url(r'^entrar/$', entrar),
    url(r'^salir/$', salir),
)