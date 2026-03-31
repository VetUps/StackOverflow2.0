from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from drf_spectacular.types import OpenApiTypes
from rest_framework import viewsets, status, mixins, pagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Question, Solution, SolutionEdits
from .serializers import (
    QuestionGetSerializer, QuestionListSerializer, QuestionUpdateCreateSerializer,
    SolutionListSerializer, SolutionCreateSerializer,
    SolutionEditCreateSerializer, SolutionEditHistorySerializer,
)
from .services.solution_edits_service import SolutionEditService

class QuestionViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    queryset = Question.objects.all()
    pagination_class = pagination.PageNumberPagination

    question_get_serializer = QuestionGetSerializer
    question_list_serializer = QuestionListSerializer
    question_create_serializer = QuestionUpdateCreateSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return self.question_list_serializer
        if self.action == 'retrieve':
            return self.question_get_serializer
        if self.action in ['create', 'update', 'partial_update']:
            return self.question_create_serializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

class SolutionViewSet(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      viewsets.GenericViewSet):
    pagination_class = pagination.PageNumberPagination

    solution_list_serializer = SolutionListSerializer
    solution_create_serializer = SolutionCreateSerializer

    def get_queryset(self):
        if self.action == 'list':
            return Solution.objects.filter(question__question_id=self.request.query_params.get('question_id'))
        return Solution.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return self.solution_list_serializer
        if self.action == 'create':
            return self.solution_create_serializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                'question_id', OpenApiTypes.UUID,
                      location='query', required=True, description='ID вопроса'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

class SolutionEditsViewSet(mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    solution_edit_create_serializer = SolutionEditCreateSerializer

    def get_queryset(self):
        return SolutionEdits.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return self.solution_edit_create_serializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'approve', 'disapprove', 'not_approved']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        solution = serializer.validated_data['solution']
        user = self.request.user
        is_author = solution.user == user

        serializer.save(
            user=self.request.user,
            solution_edit_is_approved=True if is_author else None
        )

        if is_author:
            solution.solution_body = serializer.validated_data['solution_edit_body_after']
            solution.save(update_fields=['solution_body', 'solution_updated_at'])

    @action(detail=False, methods=['get'], url_path='history/(?P<solution_id>[^/.]+)')
    def history(self, request, solution_id):
        result = SolutionEditService.history(solution_id)
        serializer = SolutionEditHistorySerializer(result, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['get'], url_path='not_approved/(?P<solution_id>[^/.]+)')
    def not_approved(self, request, solution_id):
        user = request.user
        result = SolutionEditService.not_approved(solution_id, user)
        serializer = SolutionEditHistorySerializer(result, many=True)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(detail=False, methods=['post'], url_path='approve/(?P<solution_edit_id>[^/.]+)')
    def approve(self, request, solution_edit_id):
        user = request.user
        SolutionEditService.change_approve(solution_edit_id, True, user)

        return Response(
            {'approved': True},
            status=status.HTTP_200_OK
        )

    @action(detail=False, methods=['post'], url_path='disapprove/(?P<solution_edit_id>[^/.]+)')
    def disapprove(self, request, solution_edit_id):
        user = request.user
        SolutionEditService.change_approve(solution_edit_id, False, user)

        return Response(
            {'approved': False},
            status=status.HTTP_200_OK
        )
