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
                solution_id=solution_id
            )

            return solution
        except Solution.DoesNotExist:
            raise NotFound('Такого решения не существует')

    @staticmethod
    def change_solution_body(solution, new_body):
        """
        Изменяет содержимое решения
        :param solution: решение
        :param new_body: новое содержимое
        :return:
        """
        Solution.objects.filter(solution_id=solution.solution_id).update(solution_body=new_body)