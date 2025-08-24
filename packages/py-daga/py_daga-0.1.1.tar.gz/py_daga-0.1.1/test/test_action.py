import pytest
from typing import NamedTuple

from src.action import DagaAction


class Increase(DagaAction[int, int]):
    async def __call__(self, input: int) -> int:
        return input + 1


@Increase.register_class_as_rollback
class Decrease(DagaAction[int, int]):
    async def __call__(self, input: int) -> int:
        return input - 1


class AppenderInput(NamedTuple):
    l: list[int]
    i: int


class AppendInt(DagaAction[AppenderInput, list[int]]):
    async def __call__(self, input: AppenderInput) -> list[int]:
        input.l.append(input.i)
        raise Exception("let's say this action failed")
        return input.l


@AppendInt.register_class_as_rollback
class RemoveInt(DagaAction[AppenderInput, list[int]]):
    async def __call__(self, input: AppenderInput) -> list[int]:
        input.l.remove(input.i)
        return input.l


class TestDagaActions:
    """Test cases for DagaAction functionality"""
    
    @pytest.mark.asyncio
    async def test_increase_action(self):
        """Test that Increase action correctly increments the input"""
        action = Increase()
        result = await action(2)
        assert result == 3
    
    @pytest.mark.asyncio
    async def test_increase_rollback(self):
        """Test that Increase rollback (Decrease) correctly decrements the input"""
        action = Increase()
        result = await action(2)  # Should be 3
        rollback_result = await action.rollback(result)
        assert rollback_result == 2
    
    @pytest.mark.asyncio
    async def test_append_int_action_fails(self):
        """Test that AppendInt action fails as expected"""
        test_list = []
        appender = AppendInt()
        
        with pytest.raises(Exception, match="let's say this action failed"):
            await appender(AppenderInput(l=test_list, i=1))
        
        # The list should still have 1 in it since the action failed after the append
        assert test_list == [1]

    @pytest.mark.asyncio
    async def test_saga_action_chain(self):
        """Test a chain of saga actions with rollback"""
        # Test multiple increases and their rollbacks
        action = Increase()
        
        # Execute multiple times
        result1 = await action(1)  # Should be 2
        result2 = await action(result1)  # Should be 3
        result3 = await action(result2)  # Should be 4
        
        assert result1 == 2
        assert result2 == 3
        assert result3 == 4
        
        # Rollback in reverse order
        rollback3 = await action.rollback(result3)  # Should be 3
        rollback2 = await action.rollback(result2)  # Should be 2
        rollback1 = await action.rollback(result1)  # Should be 1
        
        assert rollback3 == 3
        assert rollback2 == 2
        assert rollback1 == 1
