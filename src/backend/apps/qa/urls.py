from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet

app_name = 'question'

router = DefaultRouter()
router.register('question', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
]