"""
Utility functions and classes for DAG flow orchestration.

This module provides utility functions and data structures for managing
DAG-based workflows, including action descriptors, batches, and flow utilities.
"""

from dataclasses import dataclass
import time
import networkx as nx
from typing import Any, Callable, Iterable

from src.action import DagaAction, EmptyAction


def indexx[T, I](iterable: Iterable[Iterable[T]], item: I, key: Callable[[T], I] = lambda x: x) -> tuple[int, int]:
    """
    Find the position of an item in a nested iterable.
    
    Args:
        iterable: A nested iterable (e.g., list of lists)
        item: The item to search for
        key: Function to extract the key from each item for comparison
    
    Returns:
        Tuple of (outer_index, inner_index) where the item was found
    
    Raises:
        KeyError: If the item is not found in the iterable
    """
    for i, sub_iterable in enumerate(iterable):
        for j, v in enumerate(sub_iterable):
            if key(v) == item:
                return i, j
    raise KeyError(f"Item {item} not found in iterable")


BatchID = int
NodeID = int


@dataclass
class ActionDescriptor[I, O]:
    """
    Descriptor for an action in a workflow batch.
    
    This class holds metadata about an action including its position in the
    workflow, timing information, and execution results.
    
    Generic Parameters:
        I: Input type for the action
        O: Output type of the action
    
    Attributes:
        action: The DagaAction instance
        batch_index: Index of the batch this action belongs to
        node_index: Index of the node within the batch
        predecessors: List of (batch_index, node_index) tuples for predecessor actions
        result: The result of executing this action (None if not yet executed)
        time_started: Timestamp when execution started (None if not yet started)
        time_ended: Timestamp when execution ended (None if not yet ended)
        error: Exception that occurred during execution (None if successful)
    """
    action: DagaAction[I, O]
    batch_index: BatchID
    node_index: NodeID
    predecessors: list[tuple[BatchID, NodeID]]
    result: O | None = None
    time_started: float | None = None
    time_ended: float | None = None
    error: Exception | None = None


class Batch[I, O](list[ActionDescriptor[I, O]]):
    """
    A batch of actions that can be executed in parallel.
    
    This class represents a collection of actions that have no dependencies
    on each other and can therefore be executed concurrently.
    
    Generic Parameters:
        I: Input type for the actions in this batch
        O: Output type of the actions in this batch
    """
    
    def results(self) -> list[O]:
        """
        Get the results of all actions in this batch.
        
        Returns:
            List of results from all actions in the batch
        """
        return [action.result for action in self]


class DagaFlowUtils:
    """
    Utility class for managing DAG-based workflow execution.
    
    This class provides static methods for converting DAGs into executable
    batches, managing action execution, and handling rollback operations.
    """
    
    @staticmethod
    def get_predecessors_results(action: ActionDescriptor[Any, Any], batches: list[Batch[Any, Any]]) -> list[Any]:
        """
        Get the results of all predecessor actions for a given action.
        
        Args:
            action: The action descriptor to get predecessors for
            batches: List of all batches in the workflow
        
        Returns:
            List of results from predecessor actions
        """
        return [
            batches[batch_index][node_index].result 
            for batch_index, node_index 
            in action.predecessors
        ]
    
    @staticmethod
    def initialize_dag_as_flow(dag: nx.DiGraph, root: DagaAction[Any, Any] = EmptyAction()):
        """
        Initialize a DAG by adding a root action to nodes with no incoming edges.
        
        This method ensures that all nodes in the DAG have at least one
        predecessor by connecting nodes with no incoming edges to a root action.
        
        Args:
            dag: The NetworkX DiGraph representing the workflow
            root: The root action to use (defaults to EmptyAction)
        """
        dag.add_edges_from([(root, node) for node in dag if not dag.in_degree(node)])

    @staticmethod
    def get_flow_batches(dag: nx.DiGraph) -> list[Batch[Any, Any]]:
        """
        Convert a DAG into a list of executable batches.
        
        This method performs topological sorting to determine the execution
        order and creates ActionDescriptor objects for each action.
        
        Args:
            dag: The NetworkX DiGraph representing the workflow
        
        Returns:
            List of batches, where each batch contains actions that can be
            executed in parallel
        """
        batches: list[Batch[Any, Any]] = list(nx.topological_generations(dag))
        # replace the actions in the batches with ActionDescriptors
        for batch_index, batch in enumerate(batches):
            for node_index, action in enumerate(batch):
                predecessors = [indexx(batches, predecessor, key=lambda x: x.action) for predecessor in dag.predecessors(action)]
                batches[batch_index][node_index] = ActionDescriptor(action, batch_index, node_index, predecessors)
        return batches

    @staticmethod
    async def wrap_action(action: ActionDescriptor[Any, Any], batches: list[Batch[Any, Any]]) -> ActionDescriptor[Any, Any]:
        """
        Execute an action with proper timing and error handling.
        
        This method executes an action, records timing information, and
        handles any exceptions that occur during execution.
        
        Args:
            action: The action descriptor to execute
            batches: List of all batches in the workflow
        
        Returns:
            The action descriptor with updated result and timing information
        
        Raises:
            Exception: Any exception that occurs during action execution
        """
        action.time_started = time.time()
        try:
            predecessors_results = DagaFlowUtils.get_predecessors_results(action, batches)
            action.result = await action.action(predecessors_results)
            return action.result
        except Exception as e:
            action.error = e
            raise e
        finally:
            action.time_ended = time.time()

    @staticmethod
    async def rollback_action(action: ActionDescriptor[Any, Any], batches: list[Batch[Any, Any]]) -> Any:
        """
        Execute the rollback for a given action.
        
        This method executes the rollback action associated with the given
        action descriptor.
        
        Args:
            action: The action descriptor to rollback
            batches: List of all batches in the workflow
        
        Returns:
            The result of the rollback operation
        """
        return await action.action.rollback(DagaFlowUtils.get_predecessors_results(action, batches))
