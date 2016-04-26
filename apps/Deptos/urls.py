from django.conf.urls import include, url, patterns
from .views import NuevoDepto, VerDeptos, Home

urlpatterns = patterns('',
    url(r'^home/$', Home.as_view()),
    url(r'^nuevo/$', NuevoDepto.as_view()),
    url(r'^lista/$', VerDeptos.as_view()),
    url(r'^pedido/', include('apps.Pedido.urls')),
)