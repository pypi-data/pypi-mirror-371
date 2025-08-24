# Daga - Saga DAGs Made Easy
A simple, standard library-based tool to create and run Saga pattern mission DAGs. 
Need an atomic way to create real world objects? This is the way. 
No more try-excepts and nested logic - focus on your bussiness.

## Docs & Usage
See the package generated documentation at https://river-studio-net.github.io/py-daga/

## Contributing
### Documentation
The project includes comprehensive auto-generated documentation that is updated automatically on every push to the main branch.

#### Auto-Generation
The documentation in the `docs/` folder is automatically generated using [pdoc](https://pdoc.dev/) whenever changes are pushed to the main branch. The GitHub Action workflow (`.github/workflows/docs.yml`) handles this process.

#### Viewing Documentation
Open `docs/index.html` in your web browser to view the generated documentation.

#### Documentation Structure
- `index.html` - Main documentation page with module overview
- `action.html` - Documentation for the DagaAction classes
- `flow.html` - Documentation for the DagaFlow orchestrator
- `meta.html` - Documentation for the DagaMeta metaclass
- `utils.html` - Documentation for utility functions and classes

### Development
To contribute to the project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass: `uv run pytest`
6. Submit a pull request

## Rejected Ideas
### Implmenting DagaAction as a context manager
Trying to use said context manager proved to be confusing beyond any standard, and so it has been decided to drop the implementation.
Another concern against the idea was that it added significant complexity to the codebase, adding a lot of functionality that was not used otherwise. 

### Implementing rollbacks with Python `results` module
I didn't want to add extra dependency and added complexity on top of everything.