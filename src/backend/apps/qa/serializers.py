from rest_framework import serializers
from .models import Question, Solution


class QuestionGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['user', 'question_title', 'question_status', 'question_created_at', 'question_updated_at']

class QuestionCreateSerializer(serializers.Serializer):
    user = serializers.UUIDField(write_only=True)

    class Meta:
        model = Question
        fields = ['user', 'question_title', 'question_body']

class SolutionGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = '__all__'

class SolutionCreateSerializer(serializers.Serializer):
    user = serializers.UUIDField(write_only=True)

    class Meta:
        model = Solution
        fields = ['user', 'solution_body']