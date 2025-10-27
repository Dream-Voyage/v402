# Contributing to v402

Thank you for your interest in contributing to v402! This document provides guidelines and instructions for contributing.

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please be respectful and constructive in all interactions.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please create an issue describing:
- The problem you're trying to solve
- Your proposed solution
- Any alternative approaches considered
- Potential impact on existing functionality

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Write tests** for new functionality
5. **Update documentation** as needed
6. **Run tests**: `pytest`
7. **Run linters**: `black . && ruff check .`
8. **Commit changes**: Use clear, descriptive commit messages
9. **Push to your fork**: `git push origin feature/your-feature-name`
10. **Create a Pull Request**

### Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/v402.git
cd v402

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
pip install -e ./v402_index_client
pip install -e ./v402_content_provider
pip install -e ./v402_facilitator

# Install pre-commit hooks (optional)
pre-commit install
```

### Coding Standards

- **Python Version**: 3.10+
- **Code Style**: Follow PEP 8, use Black for formatting
- **Type Hints**: Use type hints for all function signatures
- **Documentation**: Use docstrings for all public functions/classes
- **Comments**: Use English for all code comments
- **Naming**: Use descriptive names, follow Python conventions

### Testing

- Write unit tests for all new functionality
- Ensure all tests pass before submitting PR
- Aim for >80% code coverage
- Include integration tests where appropriate

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=v402_index_client --cov=v402_content_provider --cov=v402_facilitator

# Run specific test file
pytest tests/test_client.py
```

### Documentation

- Update README.md for major changes
- Add docstrings to all public APIs
- Update examples if APIs change
- Keep documentation in sync with code

### Commit Message Guidelines

Use conventional commits format:

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build process or auxiliary tool changes

Example:
```
feat(client): add batch request support

Added batch_get() method to V402IndexClient for processing
multiple URLs concurrently with automatic payment handling.

Closes #123
```

### Review Process

1. All PRs require at least one review
2. Address review comments promptly
3. Keep PRs focused and reasonably sized
4. Ensure CI/CD checks pass
5. Maintain backwards compatibility when possible

### Architecture Guidelines

#### v402_index_client
- Keep the client stateless where possible
- Handle errors gracefully with clear messages
- Implement retry logic for network failures
- Track all payments for transparency

#### v402_content_provider
- Support multiple web frameworks
- Make integration as simple as possible
- Provide clear error messages for misconfiguration
- Ensure payment verification is secure

#### v402_facilitator
- Prioritize security in all operations
- Implement proper error handling
- Log all important events
- Design for horizontal scalability
- Use database transactions appropriately

### Security

- Never commit private keys or secrets
- Use environment variables for sensitive data
- Implement proper input validation
- Follow security best practices for blockchain interactions
- Report security vulnerabilities privately

### Performance

- Consider performance impact of changes
- Profile code for bottlenecks
- Use async/await appropriately
- Optimize database queries
- Cache when beneficial

### Questions?

Feel free to:
- Open an issue for questions
- Join our community discussions
- Reach out to maintainers

Thank you for contributing to v402! 🎉

