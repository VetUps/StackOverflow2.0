from rest_framework.exceptions import NotFound
from ..models import Solution

class SolutionService:
    @staticmethod
    def get_solution(solution_id):
        """
        Возвращает решение по его ID
        :param solution_id: ID решения
        :return:
        """
        try:
            solution = Solution.objects.get(
                id=solution_id
            )

            return solution
        except Solution.DoesNotExist:
            raise NotFound('Такого решения не существует')