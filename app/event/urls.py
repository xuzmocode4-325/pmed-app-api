"""
URL mappings for the event app.
"""
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('events', views.EventViewSet)
router.register('procedures', views.ProcedureViewSet)
router.register('allocations', views.AllocationViewSet)

app_name = 'event'

urlpatterns = [
    path('', include(router.urls)),
]