"""
DagaMeta metaclass for managing DagaAction registration and validation.

This module provides the metaclass that handles the registration and validation
of DagaAction classes to ensure proper workflow construction.
"""

from typing import final


@final
class DagaMeta(type):
    """
    Metaclass for DagaAction classes that handles registration and validation.
    
    This metaclass ensures that all DagaAction classes are properly registered
    and that inheritance relationships are valid. It prevents duplicate action
    names and ensures that base classes are also registered actions.
    
    Attributes:
        REGISTERED_ACTIONS: Dictionary mapping action names to their class types
        RESERVED_ACTION_NAMES: List of names that are reserved and not registered
    """
    REGISTERED_ACTIONS: dict[str, type] = {}
    RESERVED_ACTION_NAMES: list[str] = ["DagaAction", "EmptyAction", "DagaMeta"]
    
    def __new__(cls, name, bases, attrs):
        """
        Create a new DagaAction class with registration and validation.
        
        Args:
            name: The name of the class being created
            bases: Tuple of base classes
            attrs: Dictionary of class attributes
        
        Returns:
            The newly created class
        
        Raises:
            TypeError: If the action name is already registered or if base classes
                      are not registered actions
        """
        new_cls = super().__new__(cls, name, bases, attrs)
        if name in cls.RESERVED_ACTION_NAMES:
            return new_cls
        if name not in cls.REGISTERED_ACTIONS:
            cls.REGISTERED_ACTIONS[name] = new_cls
        else:
            raise TypeError(f"Action {name} already registered")
        for base in bases:
            if base.__class__.__name__ in cls.RESERVED_ACTION_NAMES:
                continue
            if base not in cls.REGISTERED_ACTIONS and base.__class__.__name__ not in cls.RESERVED_ACTION_NAMES:
                raise TypeError(f"Base class {base} for DagaAction {name} is not a registered action")
        return new_cls

    @classmethod
    def clear_registered_actions(cls):
        """
        Clear all registered actions.
        
        This method is useful for testing or when you need to reset the
        action registry.
        """
        cls.REGISTERED_ACTIONS = {}

    @classmethod
    def get_registered_actions(cls) -> dict[str, type]:
        """
        Get all currently registered actions.
        
        Returns:
            Dictionary mapping action names to their class types
        """
        return cls.REGISTERED_ACTIONS
