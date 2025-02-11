"""
URL mappings for the event app.
"""
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('eventss', views.EventViewSet)

app_name = 'event'

urlpatterns = [
    path('', include(router.urls)),
]