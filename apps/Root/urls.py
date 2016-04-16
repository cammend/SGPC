from django.conf.urls import include, url, patterns
from .views import root
from apps.Estado.views import addEstadoDepto

urlpatterns = patterns('',
	url(r'^$', root),
	url(r'^asociar/$', addEstadoDepto),
)