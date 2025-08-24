import pytest

from src.action import DagaAction
from src.meta import DagaMeta


class TestDagaActionCreation:
    @pytest.fixture(autouse=True)
    def setup_class(self):
        DagaMeta.clear_registered_actions()
        yield
    
    def test_creation_by_class(self):
        class Increase(DagaAction[int, int]):
            async def __call__(self, input: int) -> int:
                return input + 1

        assert f"{Increase()}" == "DagaAction(Increase)"

    def test_creation_by_class_with_rollback(self):
        class Increase(DagaAction[int, int]):
            async def __call__(self, input: int) -> int:
                return input + 1

        @Increase.register_class_as_rollback
        class Decrease(DagaAction[int, int]):
            async def __call__(self, input: int) -> int:
                return input - 1

        assert f"{Increase._wrapped_action_instance}" == "DagaAction(Decrease)"

    def test_creation_by_decorator(self):
        @DagaAction[int, int]
        def increase(input: int) -> int:
            return input + 1

        assert f"{increase}" == "DagaAction(increase)"

    def test_creation_by_decorator_with_rollback(self):
        @DagaAction[int, int]
        def increase(input: int) -> int:
            return input + 1

        assert f"{increase}" == "DagaAction(increase)", "The action should be created by the decorator"

        @increase.register_function_as_rollback
        @DagaAction[int, int]
        def decrease(input: int) -> int:
            return input - 1

        assert f"{increase}" == "DagaAction(increase)", "The action name should not be changed"
        assert f"{increase._wrapped_action_instance}" == "DagaAction(decrease)"

    def test_manual_creation(self):
        def increase(input: int) -> int:
            return input + 1

        increase = DagaAction[int, int](increase)
        assert f"{increase}" == "DagaAction(increase)"

    def test_manual_creation_with_rollback(self):
        def increase(input: int) -> int:
            return input + 1

        increase = DagaAction[int, int](increase)
        assert f"{increase}" == "DagaAction(increase)"

        def decrease(input: int) -> int:
            return input - 1

        increase.register_function_as_rollback(DagaAction[int, int](decrease))
        assert f"{increase._wrapped_action_instance}" == "DagaAction(decrease)"
