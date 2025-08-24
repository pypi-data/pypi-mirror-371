"""
DagaFlow module for orchestrating DAG-based workflow execution.

This module provides the main orchestrator class for executing workflows
defined as directed acyclic graphs (DAGs) with support for rollback mechanisms.
"""

import asyncio
import networkx as nx

from src.utils import DagaFlowUtils


class DagaFlow[I, O]:
    """
    Orchestrator for executing DAG-based workflows with rollback support.
    
    DagaFlow takes a directed acyclic graph (DAG) of actions and executes them
    in the correct order, handling failures and performing rollbacks when necessary.
    Actions within the same batch are executed in parallel for efficiency.
    
    Generic Parameters:
        I: Input type for the workflow
        O: Output type of the workflow
    
    Attributes:
        dag: The NetworkX DiGraph representing the workflow
        action_matrix: List of batches containing ActionDescriptor objects
    """
    
    def __init__(self, dag: nx.DiGraph):
        """
        Initialize a DagaFlow instance with a DAG.
        
        Args:
            dag: A NetworkX DiGraph where nodes are DagaAction instances and
                 edges represent dependencies between actions
        
        Raises:
            AssertionError: If the provided graph is not a directed acyclic graph
        """
        self.dag = dag
        assert nx.is_directed_acyclic_graph(self.dag), "DAG must be a directed acyclic graph"
        DagaFlowUtils.initialize_dag_as_flow(self.dag)
        self.action_matrix = DagaFlowUtils.get_flow_batches(self.dag)

    def __repr__(self):
        """Return a string representation of this DagaFlow instance."""
        return f"DagaFlow({self.dag})"

    def __str__(self):
        """Return a string representation of this DagaFlow instance."""
        return self.__repr__()
    
    async def run(self, input: I) -> list[O]:
        """
        Execute the workflow with the given input.
        
        This method executes all actions in the workflow in the correct order,
        with parallel execution within batches. If any action fails, the workflow
        performs rollback operations for all affected actions.
        
        Args:
            input: The initial input value for the workflow
        
        Returns:
            List of results from the final batch of actions
        
        Raises:
            ExceptionGroup: If any action fails, containing all the errors
                           that occurred during execution
        """
        self.action_matrix[0][0].result = input
        for batch_index, batch in enumerate(self.action_matrix[1:], start=1):
            tasks = [DagaFlowUtils.wrap_action(action, self.action_matrix) for action in batch]
            await asyncio.gather(*tasks, return_exceptions=True)
            failed_actions = list(filter(lambda x: x.error, batch))
            if failed_actions:
                for failed_action in failed_actions:
                    await DagaFlowUtils.rollback_action(failed_action, self.action_matrix)
                for batch in self.action_matrix[batch_index:]:
                    rollback_tasks = [DagaFlowUtils.rollback_action(action, self.action_matrix) for action in batch]
                    await asyncio.gather(*rollback_tasks)
                raise ExceptionGroup("DagaFlowError", [failed_action.error for failed_action in failed_actions])
        return [action.result for action in self.action_matrix[-1]]
