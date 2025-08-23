"""
High-level manager classes for Fluidize resources.

This module provides a clean abstraction layer for managing Fluidize projects
and their associated resources. The architecture follows a clear hierarchy
designed to make common workflows intuitive while maintaining flexibility
for advanced use cases.

Architecture Overview:
    The managers module implements a two-tier pattern:

    1. **Global Managers** - Handle cross-project operations
       - `RegistryManager`: Creates, retrieves, updates, and lists projects

    2. **Project-Scoped Managers** - Bound to specific projects
       - `GraphManager`: Manages nodes and edges within a project's computational graph
       - `RunsManager`: Executes and monitors workflow runs for a project

Design Pattern:
    The module uses a wrapper pattern where global managers return entity
    objects that provide convenient access to scoped operations::

        client.projects (Projects)
            └── .create() / .get() → Project entity
                    ├── .graph (GraphManager) - Computational graph operations
                    └── .runs (RunsManager) - Workflow execution operations

Usage Examples:
    Basic project workflow::

        >>> from fluidize import FluidizeClient
        >>> client = FluidizeClient(mode="local")

        # Global manager creates project
        >>> project = client.projects.create(
        ...     project_id="cfd-sim",
        ...     label="CFD Simulation",
        ...     description="Fluid dynamics analysis"
        ... )

        # Project entity provides scoped managers
        >>> node = project.graph.add_node(node_data)
        >>> result = project.runs.run_flow(payload)

    Managing multiple projects::

        >>> # List all projects
        >>> projects = client.projects.list()
        >>> for p in projects:
        ...     print(f"{p.id}: {p.label}")

        >>> # Update existing project
        >>> updated = client.projects.update(
        ...     "cfd-sim",
        ...     status="completed"
        ... )

    Graph operations::

        >>> project = client.projects.get("my-project")
        >>> graph_data = project.graph.get()
        >>> project.graph.add_node(simulation_node)
        >>> project.graph.add_edge(connection_edge)
        >>> ascii_viz = project.graph.show()

    Running workflows::

        >>> project = client.projects.get("my-project")
        >>> payload = RunFlowPayload(
        ...     name="simulation-run",
        ...     description="CFD analysis run"
        ... )
        >>> result = project.runs.run_flow(payload)
        >>> status = project.runs.get_status(result["run_number"])

File Structure:
    - `projects.py`: Global project CRUD operations (Projects class)
    - `project_manager.py`: Single project entity with sub-managers (Project class)
    - `graph.py`: Project-scoped graph operations (GraphManager class)
    - `runs.py`: Project-scoped run operations (RunsManager class)

Threading and adapter Support:
    All managers are thread-safe and support both local filesystem and
    cloud API adapters through the underlying adapter pattern. The choice
    of adapter is transparent to the manager classes.

See Also:
    - :class:`~fluidize.managers.registry.RegistryManager`: Global project manager
    - :class:`~fluidize.managers.project.ProjectManager`: Project entity wrapper
    - :class:`~fluidize.managers.graph.GraphManager`: Graph operations
    - :class:`~fluidize.managers.runs.RunsManager`: Run operations
"""
