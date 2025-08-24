import pytest
import networkx as nx
from unittest.mock import AsyncMock, MagicMock

from src.utils import indexx, DagaFlowUtils, ActionDescriptor, Batch
from src.action import EmptyAction


class TestUtils:
    """Test cases for Utils functionality"""
    @pytest.fixture
    def test_data(self):
        return [[1, 2, 3], [4, 5, 6]]
    
    def test_indexx(self, test_data):
        assert indexx(test_data, 3) == (0, 2)
    
    def test_indexx_with_key(self, test_data):
        assert indexx(test_data, 6, key=lambda x: x * 2) == (0, 2)

    def test_indexx_with_key_and_item_not_found(self, test_data):
        with pytest.raises(KeyError):
            indexx(test_data, 7)


class TestDagaFlowUtils:
    @pytest.fixture
    def sample_actions(self):
        """Create sample actions for testing using mock objects"""
        # Create mock actions that behave like DagaAction instances
        action1 = MagicMock()
        action1.__repr__ = lambda self: "TestAction1"
        action1.__str__ = lambda self: "TestAction1"
        action1.__hash__ = lambda self: hash("TestAction1")
        
        action2 = MagicMock()
        action2.__repr__ = lambda self: "TestAction2"
        action2.__str__ = lambda self: "TestAction2"
        action2.__hash__ = lambda self: hash("TestAction2")
        
        action3 = MagicMock()
        action3.__repr__ = lambda self: "TestAction3"
        action3.__str__ = lambda self: "TestAction3"
        action3.__hash__ = lambda self: hash("TestAction3")
        
        return action1, action2, action3
    
    @pytest.fixture
    def sample_batches(self, sample_actions):
        """Create sample batches for testing"""
        action1, action2, action3 = sample_actions
        
        # Create action descriptors
        desc1 = ActionDescriptor(action1, 0, 0, [])
        desc2 = ActionDescriptor(action2, 1, 0, [(0, 0)])
        desc3 = ActionDescriptor(action3, 1, 1, [(0, 0)])
        
        # Set results
        desc1.result = "result1"
        desc2.result = "result2"
        desc3.result = "result3"
        
        batch1 = Batch([desc1])
        batch2 = Batch([desc2, desc3])
        
        return [batch1, batch2]
    
    @pytest.fixture
    def sample_dag(self, sample_actions):
        """Create a sample DAG for testing"""
        action1, action2, action3 = sample_actions
        dag = nx.DiGraph()
        dag.add_nodes_from([action1, action2, action3])
        dag.add_edges_from([(action1, action2), (action1, action3)])
        return dag

    def test_get_predecessors_results(self, sample_batches):
        """Test getting predecessor results from action descriptors"""
        # Test action with one predecessor
        action_desc = sample_batches[1][0]  # action2 with predecessor action1
        results = DagaFlowUtils.get_predecessors_results(action_desc, sample_batches)
        assert results == ["result1"]
        
        # Test action with no predecessors
        action_desc_no_pred = sample_batches[0][0]  # action1 with no predecessors
        results = DagaFlowUtils.get_predecessors_results(action_desc_no_pred, sample_batches)
        assert results == []
        
        # Test action with multiple predecessors
        # Create a new action with multiple predecessors
        action4 = MagicMock()
        action4.__repr__ = lambda self: "TestAction4"
        action4.__str__ = lambda self: "TestAction4"
        action4.__hash__ = lambda self: hash("TestAction4")
        
        desc4 = ActionDescriptor(action4, 2, 0, [(0, 0), (1, 0), (1, 1)])
        desc4.result = "result4"
        batch3 = Batch([desc4])
        sample_batches.append(batch3)
        
        results = DagaFlowUtils.get_predecessors_results(desc4, sample_batches)
        assert results == ["result1", "result2", "result3"]

    def test_initialize_dag_as_flow(self, sample_dag):
        """Test initializing DAG as flow by adding root connections"""
        # Count nodes without incoming edges before
        nodes_without_incoming = [node for node in sample_dag if sample_dag.in_degree(node) == 0]
        assert len(nodes_without_incoming) == 1  # action1
        
        # Initialize with default EmptyAction
        DagaFlowUtils.initialize_dag_as_flow(sample_dag)
        
        # Check that EmptyAction was added and connected to nodes without incoming edges
        empty_action = None
        for node in sample_dag:
            if isinstance(node, EmptyAction):
                empty_action = node
                break
        
        assert empty_action is not None
        assert sample_dag.has_edge(empty_action, nodes_without_incoming[0])
        
        # Test with custom root
        dag2 = nx.DiGraph()
        dag2.add_nodes_from([list(sample_dag.nodes())[0], list(sample_dag.nodes())[1]])
        dag2.add_edge(list(sample_dag.nodes())[0], list(sample_dag.nodes())[1])
        
        custom_root = EmptyAction()
        DagaFlowUtils.initialize_dag_as_flow(dag2, custom_root)
        
        # Check that custom root was added and connected
        assert custom_root in dag2
        assert dag2.has_edge(custom_root, list(sample_dag.nodes())[0])

    def test_get_flow_batches(self, sample_dag):
        """Test getting flow batches from DAG"""
        batches = DagaFlowUtils.get_flow_batches(sample_dag)
        
        # Should have 2 batches: first batch with action1, second with action2 and action3
        assert len(batches) == 2
        assert len(batches[0]) == 1  # First batch has 1 action
        assert len(batches[1]) == 2  # Second batch has 2 actions
        
        # Check that actions are converted to ActionDescriptors
        assert isinstance(batches[0][0], ActionDescriptor)
        assert isinstance(batches[1][0], ActionDescriptor)
        assert isinstance(batches[1][1], ActionDescriptor)
        
        # Check batch and node indices
        assert batches[0][0].batch_index == 0
        assert batches[0][0].node_index == 0
        assert batches[1][0].batch_index == 1
        assert batches[1][0].node_index == 0
        assert batches[1][1].batch_index == 1
        assert batches[1][1].node_index == 1
        
        # Check predecessors
        assert batches[0][0].predecessors == []  # Root action has no predecessors
        assert batches[1][0].predecessors == [(0, 0)]  # action2 depends on action1
        assert batches[1][1].predecessors == [(0, 0)]  # action3 depends on action1

    @pytest.mark.asyncio
    async def test_wrap_action(self, sample_batches):
        """Test wrapping an action with timing and result execution"""
        # Create a mock action
        mock_action = AsyncMock()
        mock_action.return_value = "test_result"
        
        # Create action descriptor
        action_desc = ActionDescriptor(mock_action, 1, 0, [(0, 0)])
        
        # Wrap the action
        result = await DagaFlowUtils.wrap_action(action_desc, sample_batches)
        
        # Check that the action was called with predecessor results
        mock_action.assert_called_once_with(["result1"])
        
        # Check that timing was recorded
        assert action_desc.time_started is not None
        assert action_desc.time_ended is not None
        assert action_desc.time_ended > action_desc.time_started
        
        # Check that result was set
        assert action_desc.result == "test_result"
        assert result == "test_result"
        
        # Test with action that has no predecessors
        action_desc_no_pred = ActionDescriptor(mock_action, 0, 0, [])
        result = await DagaFlowUtils.wrap_action(action_desc_no_pred, sample_batches)
        
        # Should be called with empty list
        mock_action.assert_called_with([])
        assert action_desc_no_pred.result == "test_result"

    @pytest.mark.asyncio
    async def test_wrap_action_with_exception(self, sample_batches):
        """Test wrapping an action that raises an exception"""
        # Create a mock action that raises an exception
        mock_action = AsyncMock()
        mock_action.side_effect = Exception("Test exception")
        
        # Create action descriptor
        action_desc = ActionDescriptor(mock_action, 1, 0, [(0, 0)])
        
        # Wrap the action and expect exception
        with pytest.raises(Exception, match="Test exception"):
            await DagaFlowUtils.wrap_action(action_desc, sample_batches)
        
        # Check that timing was recorded (time_started should be set, time_ended may not be set on exception)
        assert action_desc.time_started is not None
        # Note: time_ended is not set when an exception occurs in the current implementation
        # This could be considered a potential improvement to the wrap_action method

    def test_batch_results(self, sample_batches):
        """Test Batch.results() method"""
        batch = sample_batches[0]  # Batch with one action
        results = batch.results()
        assert results == ["result1"]
        
        batch2 = sample_batches[1]  # Batch with two actions
        results = batch2.results()
        assert results == ["result2", "result3"]

    def test_action_descriptor_creation(self):
        """Test ActionDescriptor creation and attributes"""
        action = EmptyAction()
        predecessors = [(0, 0), (1, 1)]
        
        desc = ActionDescriptor(action, 2, 3, predecessors)
        
        assert desc.action == action
        assert desc.batch_index == 2
        assert desc.node_index == 3
        assert desc.predecessors == predecessors
        assert desc.result is None
        assert desc.time_started is None
        assert desc.time_ended is None