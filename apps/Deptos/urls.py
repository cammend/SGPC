from django.conf.urls import include, url, patterns
from .views import home, NuevoDepto

urlpatterns = patterns('',
    url(r'^home/$', home),
    url(r'^nuevo/$', NuevoDepto.as_view()),
)