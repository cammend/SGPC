from django.conf.urls import include, url, patterns
from .views import home

urlpatterns = patterns('',
    url(r'^([a-zA-Z_]+)/$', home),
)