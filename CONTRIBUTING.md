# Contributing to Two-Photon Lithography

Thank you for your interest in contributing! This project is part of research at BTU Cottbus-Senftenberg and welcomes contributions from the community.

## Ways to Contribute

- 🐛 **Bug reports** - Found an issue? Open a GitHub issue
- 💡 **Feature requests** - Have an idea? We'd love to hear it
- 📝 **Documentation** - Improve or add documentation
- 🔬 **Examples** - Share your fabrication examples
- 💻 **Code** - Submit pull requests with improvements

## Getting Started

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/two-photon-lithography.git
cd two-photon-lithography
```

### 2. Set Up Development Environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e ".[dev]"
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use type hints where applicable
- Maximum line length: 100 characters
- Use docstrings for all public functions/classes

```python
def my_function(param: float) -> float:
    """
    Brief description.
    
    Parameters
    ----------
    param : float
        Parameter description
        
    Returns
    -------
    float
        Return value description
    """
    return param * 2
```

### Testing

Run tests before submitting:

```bash
# All tests
pytest tests/ -v

# Specific test
pytest tests/unit/test_geometry.py -v

# With coverage
pytest tests/ --cov=tpl --cov-report=html
```

Add tests for new features:
```python
def test_my_new_feature():
    """Test that my feature works."""
    result = my_function(5.0)
    assert result == 10.0
```

### Documentation

Update documentation for:
- New features
- API changes
- Configuration options

Documentation uses Markdown format in `docs/` directory.

## Pull Request Process

1. **Update tests** - Add/update tests for your changes
2. **Update docs** - Document new features or changes
3. **Run tests** - Ensure all tests pass
4. **Check style** - Run `black` and `flake8`
5. **Commit** - Use clear, descriptive commit messages
6. **Push** - Push to your fork
7. **PR** - Open pull request with description

### Commit Message Format

```
type: Brief description (50 chars or less)

More detailed explanation if needed. Wrap at 72 characters.

- Bullet points are okay
- Use present tense ("Add feature" not "Added feature")
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Examples**:
```
feat: Add spiral fill pattern to PathPlanner
fix: Correct laser power calibration calculation
docs: Update installation instructions
```

## Code Review

All submissions require review. We'll:
- Check code quality and style
- Verify tests pass
- Review documentation
- Test functionality

Please be patient - reviews may take a few days.

## Questions?

- **General questions**: Open a GitHub issue with "Question" label
- **Bugs**: Open a GitHub issue with bug template
- **Contact**: zeyad.mustafa@b-tu.de

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to advancing two-photon lithography research!** 🔬✨