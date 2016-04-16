from django.conf.urls import include, url, patterns
from .views import ListarCotizaciones,IngresarCotizacion


urlpatterns = patterns('',
    url(r'^lista_cotizaciones/$', ListarCotizaciones),
    url(r'^nueva_cotizacion/$', IngresarCotizacion),
)