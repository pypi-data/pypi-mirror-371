"""
DagaAction module providing the core action classes for workflow orchestration.

This module defines the base classes for creating workflow actions that can be
executed as part of a directed acyclic graph (DAG) workflow.
"""

from logging import Logger, getLogger
from typing import Any, Callable, Coroutine, final

from src.meta import DagaMeta


class DagaAction[I, O](metaclass=DagaMeta):
    """
    Base class for defining workflow actions in a DAG-based workflow system.
    
    DagaAction represents a single unit of work in a workflow. Each action can
    receive results from predecessor actions and produce output that can be
    consumed by successor actions. Actions can also have rollback functionality
    for error recovery.
    
    Generic Parameters:
        I: Input type for the action (when used as a decorator)
        O: Output type of the action
    
    Attributes:
        _wrapped_action_instance: The rollback action instance if registered
        log: Logger instance for this action
        is_decorator_action: Whether this action was created via decorator
        wrapped_func: The actual function to be executed
    """
    _wrapped_action_instance: "DagaAction[I, O]" = None
    log: Logger = getLogger(__name__)
    
    @final
    def __init__(self, wrapped: Coroutine[I, Any, O] | None = None) -> None:
        """
        Initialize a DagaAction instance.
        
        Args:
            wrapped: Optional coroutine function to wrap. If provided, this action
                    is created as a decorator action with the wrapped function.
        """
        self.is_decorator_action = False
        self.wrapped_func = self.__call__
        # wrapped is available means that the action is created by decorating a callable
        if wrapped:
            self.wrapped_func = wrapped
            self.__name__ = wrapped.__name__
            self.is_decorator_action = True
    
    def __call__(self, predecessors_results: list[Any] = None) -> Any:
        """
        Execute the action with results from predecessor actions.
        
        Args:
            predecessors_results: List of results from predecessor actions in the DAG.
                                Can be None if this is a root action.
        
        Returns:
            The result of executing this action.
        """
        return self.wrapped_func(predecessors_results)

    @final
    async def rollback(self, predecessors_results: list[Any]) -> O:
        """
        Execute the rollback action for this action.
        
        Rollback actions are used to undo the effects of a failed action or
        to clean up resources when a workflow fails.
        
        Args:
            predecessors_results: List of results from predecessor actions.
        
        Returns:
            The result of the rollback operation, or True if no rollback is defined.
        """
        if self._wrapped_action_instance:
            self.log.info(f"Rolling back {self} with {self._wrapped_action_instance}")
            return await self._wrapped_action_instance(predecessors_results) or True
        self.log.warning(f"No rollback action for {self}")
    
    @final
    @classmethod
    def register_class_as_rollback(cls, wrapped_rollback_class: type["DagaAction[I, O]"]) -> "DagaAction[I, O]":
        """
        Register a class as the rollback action for this action.
        
        Args:
            wrapped_rollback_class: The class to use as the rollback action.
                                   Must be a subclass of DagaAction.
        
        Returns:
            The registered rollback action instance.
        """
        cls._wrapped_action_instance = wrapped_rollback_class()
        return cls._wrapped_action_instance

    @final
    def register_function_as_rollback(self, wrapped_rollback_func: Callable[[Any], Coroutine[O, Any, Any]]) -> "DagaAction[I, O]":
        """
        Register a function as the rollback action for this action.
        
        Args:
            wrapped_rollback_func: The function to use as the rollback action.
                                  Must be a coroutine function.
        
        Returns:
            The registered rollback action instance.
        """
        self._wrapped_action_instance = wrapped_rollback_func
        return self._wrapped_action_instance

    @final
    def __repr__(self):
        """Return a string representation of this action."""
        return f"DagaAction({self.__class__.__name__})" if not self.is_decorator_action else f"DagaAction({self.__name__})"
    
    @final
    def __str__(self):
        """Return a string representation of this action."""
        return self.__repr__()
    
    @final
    def __hash__(self) -> int:
        """Return a hash value for this action."""
        return hash(self.__repr__())


class EmptyAction[I, O](DagaAction[I, O]):
    """
    A no-op action that simply returns its input.
    
    This action is used as a placeholder or root action in workflows
    where no actual processing is needed.
    
    Generic Parameters:
        I: Input type
        O: Output type (same as input type)
    """
    
    async def __call__(self, predecessors_results: list[Any]) -> O:
        """
        Execute the empty action.
        
        Args:
            predecessors_results: List of results from predecessor actions.
        
        Returns:
            The input value unchanged.
        """
        return predecessors_results
