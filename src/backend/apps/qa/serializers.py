from rest_framework import serializers
from .models import Question, Solution, SolutionEdits
from ..user.models import CustomUser


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
        fields = ['solution_id', 'user', 'question_id', 'solution_body', 'solution_is_best',
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

class SolutionEditCreateSerializer(serializers.ModelSerializer):
    solution = serializers.PrimaryKeyRelatedField(
        queryset=Solution.objects.all()
    )

    class Meta:
        model = SolutionEdits
        fields = ['solution', 'solution_edit_body_after']

    def validate(self, data):
        user = self.context.get('request').user
        solution = data.get('solution')

        if SolutionEdits.objects.filter(user=user, solution=solution, solution_edit_is_approved=None).exists():
            raise serializers.ValidationError('Пользователь уже выложил правку на данное решение, '
                                              'которое находится в статусе ожидания')
        return data

    def create(self, validated_data):
        original_solution = validated_data['solution']

        solution_edit = SolutionEdits.objects.create(
            solution_edit_body_before=original_solution.solution_body,
            **validated_data
        )

        return solution_edit

class SolutionEditHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SolutionEdits
        fields = '__all__'
