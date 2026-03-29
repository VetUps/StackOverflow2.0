from unittest import case

from django.contrib.auth import authenticate
from rest_framework import viewsets, status, mixins, pagination
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Question, Solution
from .serializers import (
    QuestionGetSerializer, QuestionListSerializer, QuestionUpdateCreateSerializer,
    SolutionListSerializer, SolutionCreateSerializer,
)

class QuestionViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin):
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

class SolutionViewSet(viewsets.GenericViewSet,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,):
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