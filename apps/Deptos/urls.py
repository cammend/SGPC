from django.conf.urls import include, url, patterns
from .views import home, NuevoDepto, VerDeptos

urlpatterns = patterns('',
    url(r'^home/$', home),
    url(r'^nuevo/$', NuevoDepto.as_view()),
    url(r'^lista/$', VerDeptos.as_view()),
    url(r'^pedido/', include('apps.Pedido.urls')),
)