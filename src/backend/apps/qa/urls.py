from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import QuestionViewSet, SolutionViewSet

app_name = 'qa'

router = DefaultRouter()
router.register('question', QuestionViewSet, basename='question')
router.register('solution', SolutionViewSet, basename='solution')

urlpatterns = [
    path('', include(router.urls)),
]