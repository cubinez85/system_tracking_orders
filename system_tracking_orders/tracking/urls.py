from django.urls import path
from . import views

urlpatterns = [
    path('', views.track_order, name='track_order'),
    path('api/track/', views.api_track, name='api_track'),
    path('test/', views.test, name='test'),
    path('debug/', views.debug_urls, name='debug_urls'),
]
