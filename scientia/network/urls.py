from .viewsets import GenerateEnvironmentViewSet
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'env', GenerateEnvironmentViewSet, basename='env')
urlpatterns = router.urls

app_name = 'network'

urlpatterns = [
    path("api/", include(router.urls)),

]
