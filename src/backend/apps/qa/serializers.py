from rest_framework import serializers
from .models import Question, Solution


class QuestionGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class QuestionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question_id', 'user', 'question_title', 'question_status', 'question_created_at', 'question_updated_at']

class QuestionUpdateCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question_title', 'question_body']

class SolutionListSerializer(serializers.ModelSerializer):
    question_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Solution
        fields = ['user', 'question_id', 'solution_body', 'solution_is_best',
                  'solution_created_at', 'solution_updated_at']

class SolutionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solution
        fields = ['question', 'solution_body']

    def validate(self, data):
        user = self.context.get('request').user
        question = data.get('question')

        if Solution.objects.filter(user=user, question=question).exists():
            raise serializers.ValidationError('Пользователь уже выложил решение на данный вопрос')
        return data