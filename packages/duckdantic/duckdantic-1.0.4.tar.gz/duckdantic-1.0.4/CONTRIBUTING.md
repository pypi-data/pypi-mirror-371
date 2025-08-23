# Contributing to Duckdantic

Thank you for your interest in contributing to Duckdantic! We welcome contributions from the community.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- [UV](https://github.com/astral-sh/uv) package manager
- Git

### Setting Up Development Environment

1. Fork the repository on GitHub
2. Clone your fork:

   ```bash
   git clone https://github.com/YOUR-USERNAME/duckdantic.git
   cd duckdantic
   ```

3. Install dependencies with UV:

   ```bash
   uv sync
   ```

4. Run tests to ensure everything is working:
   ```bash
   uv run pytest
   ```

## Development Workflow

### 1. Create a Branch

Create a feature branch for your changes:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-description
```

### 2. Make Your Changes

- Write clear, concise code following the project style
- Add tests for new functionality
- Update documentation as needed
- Ensure all tests pass

### 3. Code Style

We use Google-style docstrings and follow PEP 8:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed, explaining what the function
    does in more detail.

    Args:
        param1: Description of first parameter.
        param2: Description of second parameter.

    Returns:
        Description of return value.

    Raises:
        ValueError: When validation fails.

    Examples:
        Basic usage::

            result = example_function("test", 42)
            assert result is True
    """
    # Implementation
    return True
```

### 4. Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run pytest --cov=duckdantic
```

Run specific tests:

```bash
uv run pytest tests/test_specific.py
```

### 5. Linting

We use Trunk for linting and formatting:

```bash
# Format code
trunk fmt

# Check for issues
trunk check
```

### 6. Documentation

If you're adding new features or changing behavior:

1. Update relevant docstrings
2. Update documentation in `docs/`
3. Add examples if appropriate

Build documentation locally:

```bash
uv run mkdocs serve
```

Then visit http://localhost:8000 to preview.

## Submitting Changes

### 1. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add support for custom validators

- Implement custom_matcher parameter in FieldSpec
- Add tests for custom validation logic
- Update documentation with examples"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test additions/changes
- `chore:` - Maintenance tasks

### 2. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 3. Create a Pull Request

1. Go to the [Duckdantic repository](https://github.com/pr1m8/duckdantic)
2. Click "Pull Requests" → "New Pull Request"
3. Select your branch
4. Fill out the PR template with:
   - Clear description of changes
   - Related issue numbers
   - Testing performed
   - Breaking changes (if any)

## Types of Contributions

### Bug Reports

Found a bug? Please open an issue with:

- Clear description of the problem
- Minimal code example reproducing the issue
- Expected vs actual behavior
- Python version and dependencies

### Feature Requests

Have an idea? Open an issue describing:

- The problem you're trying to solve
- Your proposed solution
- Alternative approaches considered
- Example use cases

### Code Contributions

We welcome:

- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test additions
- Example code

### Documentation

Help improve our docs:

- Fix typos or unclear explanations
- Add examples
- Write tutorials
- Improve API documentation

## Code Review Process

1. All PRs require at least one review
2. CI tests must pass
3. Documentation must be updated
4. Changes should include tests

## Development Tips

### Understanding the Codebase

Key modules:

- `traits.py` - Core trait and field specifications
- `match.py` - Satisfaction checking logic
- `models.py` - Duck API implementation
- `normalize.py` - Field extraction from objects
- `providers/` - Support for different object types

### Adding a New Provider

To support a new object type:

1. Create a provider in `src/duckdantic/providers/`
2. Implement the `FieldProvider` protocol
3. Register in `providers/base.py`
4. Add tests in `tests/test_providers_detect.py`

### Performance Considerations

- Use the caching infrastructure for expensive operations
- Profile before optimizing
- Consider memory usage for large-scale applications

## Questions?

- Open a [Discussion](https://github.com/pr1m8/duckdantic/discussions) for general questions
- Check existing [Issues](https://github.com/pr1m8/duckdantic/issues) before creating new ones
- Reach out to maintainers for guidance on large changes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to Duckdantic! 🦆
