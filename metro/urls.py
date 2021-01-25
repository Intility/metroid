from django.urls import path

from metro.views import Metro

urlpatterns = [
    path('metro/deferred', Metro.as_view(), name='Metro.deferred'),
]
