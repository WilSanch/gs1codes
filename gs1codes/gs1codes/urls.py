from django.contrib import admin
from django.urls import path
from django.conf.urls import url, include
from administration.views.Index import *

urlpatterns = [
    url(r'^$', Index, name='index'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('codes/', include('administration.urls')),
    path('admin/', admin.site.urls),
    # path('prefix/', include('administration.urls')),
    url(r'^api-auth/', include('rest_framework.urls')),
]