import asyncio
from typing import Any, Optional, cast

from fluidize.core.types.project import ProjectSummary
from fluidize.core.types.runs import RunFlowPayload
from fluidize.core.utils.retrieval.handler import get_handler


class ProjectRunner:
    """
    Project runner that delegates to registered implementation based on mode.

    Follows the same pattern as DataLoader - uses get_handler() to get
    the appropriate implementation (local, cloud, etc.)
    """

    def __init__(self, project: ProjectSummary):
        """
        Args:
            project: ProjectSummary
        """
        self.project = project
        self.handler = get_handler("project_runner", project)

    def prepare_run_environment(self, metadata: RunFlowPayload) -> int:
        """
        Create a new run folder for the project.

        Args:
            metadata: RunFlowPayload

        Returns:
            int: Run number
        """
        return cast(int, self.handler.prepare_run_environment(metadata))

    async def execute_node(self, node_id: str, prev_node_id: Optional[str] = None, **kwargs: Any) -> dict[str, Any]:
        """
        Execute a single node within the project run.

        Args:
            node_id: Node ID
            prev_node_id: Previous node ID
            **kwargs: Additional keyword arguments

        Returns:
            dict[str, Any]: Execution result
        """
        return await asyncio.to_thread(self.handler.execute_node, node_id, prev_node_id=prev_node_id, **kwargs)

    async def execute_flow(self, nodes_to_run: list[str], prev_nodes: list[str], **kwargs: Any) -> list[dict[str, Any]]:
        """
        Execute a flow of nodes in order.

        Args:
            nodes_to_run: List of node IDs
            prev_nodes: List of previous node IDs
            **kwargs: Additional keyword arguments

        Returns:
            list[dict[str, Any]]: Execution results for all nodes
        """
        # Make sure that nodes_to_run and prev_nodes are same size lists
        if len(nodes_to_run) != len(prev_nodes):
            msg = "nodes_to_run and prev_nodes must be of the same length"
            raise ValueError(msg)
        return cast(list[dict[str, Any]], await self.handler.execute_flow(nodes_to_run, prev_nodes, **kwargs))
