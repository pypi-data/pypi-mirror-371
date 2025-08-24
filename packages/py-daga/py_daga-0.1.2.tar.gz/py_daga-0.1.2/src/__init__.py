"""
Py-Daga: A Python library for Directed Acyclic Graph (DAG) based workflow orchestration.

This package provides a framework for creating and executing workflows defined as directed acyclic graphs,
with support for rollback mechanisms and error handling.

## Components

- **DagaAction**: Base class for defining workflow actions
- **DagaFlow**: Orchestrator for executing DAG-based workflows

## Basic Usage Without Rollbacks

```python
import networkx as nx
from py_daga import DagaFlow

async def root(predecessors_results: list[int]):
    return sum(predecessors_results) + 1
async def layer1_f1(predecessors_results: list[int]): 
    return sum(predecessors_results) + 2
async def layer1_f2(predecessors_results: list[int]): 
    return sum(predecessors_results) + 3
async def layer2_f1(predecessors_results: list[int]): 
    return sum(predecessors_results) + 4
async def layer2_f2(predecessors_results: list[int]): 
    return sum(predecessors_results) + 5

dag = nx.DiGraph()
dag.add_edges_from([
    (root, layer1_f1),
    (root, layer1_f2),
    (layer1_f1, layer2_f1),
    (layer1_f1, layer2_f2),
    (layer1_f2, layer2_f2),
])
flow = DagaFlow(dag)
results = flow.run(input=0)  # = [7, 12]
```

## Basic Usage With Rollbacks

To use rollback functionality, we need to wrap our functions as DagaActions:

```python
import networkx as nx
from py_daga import DagaAction, DagaFlow

@DagaAction[set[str], set[str]]
async def root(predecessors_results: list[set[str]]):
    # Your action implementation here
    pass

@root.register_function_as_rollback
@DagaAction[set[str], set[str]]
async def root_rollback(predecessors_results: list[set[str]]):
    # Your rollback implementation here
    pass

@DagaAction[set[str], set[str]]
async def layer1_f1(predecessors_results: list[set[str]]): 
    # Your action implementation here
    pass

@layer1_f1.register_function_as_rollback
@DagaAction[set[str], set[str]]
async def layer1_f1_rollback(predecessors_results: list[set[str]]): 
    # Your rollback implementation here
    pass

flow = DagaFlow(
    nx.DiGraph().add_edges_from([(root, layer1_f1)])
)
results = flow.run()
```
"""

from src.action import DagaAction
from src.flow import DagaFlow

__all__ = ["DagaAction", "DagaFlow"]
