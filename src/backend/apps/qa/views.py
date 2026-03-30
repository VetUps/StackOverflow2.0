from unittest import case

from django.contrib.auth import authenticate
from rest_framework import viewsets, status, mixins, pagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiParameter

from .models import Question, Solution, SolutionEdits
from .serializers import (
    QuestionGetSerializer, QuestionListSerializer, QuestionUpdateCreateSerializer,
    SolutionListSerializer, SolutionCreateSerializer,
    SolutionEditCreateSerializer, SolutionEditHistorySerializer,
)

class QuestionViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):
    queryset = Question.objects.all()
    pagination_class = pagination.LimitOffsetPagination

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
    pagination_class = pagination.LimitOffsetPagination

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

class SolutionEditsViewSet(mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    pagination_class = None

    solution_edit_create_serializer = SolutionEditCreateSerializer

    def get_queryset(self):
        return SolutionEdits.objects.all()

    def get_serializer_class(self):
        if self.action == 'create':
            return self.solution_edit_create_serializer
        return self.serializer_class

    def get_permissions(self):
        if self.action in ['create', 'approve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]

        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='history/(?P<solution_id>[^/.]+)')
    def history(self, request, solution_id):
        try:
            solution = Solution.objects.get(solution_id=solution_id)
            solution_edits = (SolutionEdits.objects
                              .filter(solution=solution, solution_edit_is_approved=False)
                              .order_by('-solution_edit_edited_at'))

            serializer = SolutionEditHistorySerializer(solution_edits, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Solution.DoesNotExist:
            return Response(
                {'error': 'Такого решения не существует'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=['post'], url_path='approve/(?P<solution_edit_id>[^/.]+)')
    def approve(self, request, solution_edit_id):
        try:
            solution_edit = SolutionEdits.objects.get(
                solution_edit_id=solution_edit_id
            )

            if solution_edit.solution.user != request.user:
                return Response(
                    {'error': 'Вы не можете одобрять правки для данного решения'},
                    status=status.HTTP_403_FORBIDDEN
                )

            solution_edit.solution_edit_is_approved = True
            solution_edit.user = request.user
            solution_edit.save()

            return Response({'status': 'approved'}, status=status.HTTP_200_OK)

        except SolutionEdits.DoesNotExist:
            return Response(
                {'error': 'Правка не найдена'},
                status=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=False, methods=['post'], url_path='disapprove/(?P<solution_edit_id>[^/.]+)')
    def disapprove(self, request, solution_edit_id):
        try:
            solution_edit = SolutionEdits.objects.get(
                solution_edit_id=solution_edit_id
            )

            if solution_edit.solution.user != request.user:
                return Response(
                    {'error': 'Вы не можете отклонять правки для данного решения'},
                    status=status.HTTP_403_FORBIDDEN
                )

            solution_edit.solution_edit_is_approved = False
            solution_edit.user = request.user
            solution_edit.save()

            return Response({'status': 'disapproved'}, status=status.HTTP_200_OK)

        except SolutionEdits.DoesNotExist:
            return Response(
                {'error': 'Правка не найдена'},
                status=status.HTTP_404_NOT_FOUND,
            )
