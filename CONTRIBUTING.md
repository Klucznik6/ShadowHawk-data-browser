# Contributing to ShadowHawk Database Browser

Thank you for your interest in contributing to ShadowHawk Database Browser! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues
- Use the [GitHub Issues](https://github.com/Klucznik6/ShadowHawk-data-browser/issues) page
- Search existing issues before creating a new one
- Provide detailed information about the bug or feature request
- Include steps to reproduce for bugs

### Development Setup

1. **Fork and clone the repository:**
```bash
git clone https://github.com/YOUR_USERNAME/ShadowHawk-data-browser.git
cd ShadowHawk-data-browser
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the application:**
```bash
python main.py
```

### Making Changes

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Follow the existing code style
   - Add comments for complex logic
   - Update documentation if needed

3. **Test your changes:**
```bash
# Run tests
python -m pytest tests/

# Test the application manually
python main.py
```

4. **Commit your changes:**
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

5. **Push and create a Pull Request:**
```bash
git push origin feature/your-feature-name
```

## 📋 Code Style Guidelines

### Python Code Style
- Follow PEP 8 standards
- Use descriptive variable and function names
- Add docstrings for functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Example:
```python
def load_database_file(self, file_path: str) -> bool:
    """
    Load a database file and add it to the application.
    
    Args:
        file_path: Path to the database file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Implementation here
        return True
    except Exception as e:
        self.update_status(f"Error loading database: {e}")
        return False
```

### UI Guidelines
- Use emoji icons consistently (🔍 for search, 📁 for files, etc.)
- Provide user feedback for long operations
- Include confirmation dialogs for destructive actions
- Maintain responsive UI with threading for heavy operations

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_performance.py

# Run with coverage
python -m pytest tests/ --cov=.
```

### Test Structure
- Unit tests in `tests/` directory
- Test file naming: `test_*.py`
- Use descriptive test function names
- Include both positive and negative test cases

### Performance Testing
- Performance tests are in `tests/performance_test.py`
- Benchmark critical operations
- Ensure new features don't degrade performance

## 📚 Documentation

### Code Documentation
- Add docstrings to all functions and classes
- Use Google-style docstrings
- Document complex algorithms and business logic

### User Documentation
- Update README.md for new features
- Add examples for new functionality
- Update CHANGELOG.md for all changes

## 🏗️ Project Structure

```
ShadowHawk-data-browser/
├── main.py                    # Main application entry point
├── simple_browser.py          # Simplified browser version
├── config_manager.py          # Configuration management
├── polars_database_utils.py   # Polars-based data operations
├── requirements.txt           # Python dependencies
├── config.json.template       # Configuration template
├── docs/                      # Documentation
├── tests/                     # Test files
├── sample_data/               # Sample data for testing
└── scripts/                   # Utility scripts
```

## 🚀 Performance Guidelines

### Polars Integration
- Use Polars for data processing when possible
- Leverage lazy evaluation for complex operations
- Use chunking for large datasets

### Memory Management
- Monitor memory usage in operations
- Clean up resources properly
- Use generators for large data iterations

### UI Responsiveness
- Use threading for I/O operations
- Provide progress feedback for long operations
- Keep the UI thread free from heavy processing

## 🐛 Debugging

### Common Issues
1. **Import errors**: Check if all dependencies are installed
2. **Performance issues**: Profile with Polars vs pandas operations
3. **UI freezing**: Ensure heavy operations are threaded

### Debugging Tools
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Profile performance
import time
start_time = time.time()
# ... operation ...
print(f"Operation took: {time.time() - start_time:.2f} seconds")
```

## 📝 Commit Message Format

Use conventional commit format:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `perf:` for performance improvements
- `refactor:` for code refactoring
- `test:` for adding tests

Example:
```
feat: Add global search across multiple databases

- Implement search functionality in all loaded databases
- Add UI toggle for global vs single table search
- Optimize search performance with Polars integration
```

## ✅ Pull Request Checklist

Before submitting a pull request, ensure:
- [ ] Code follows the style guidelines
- [ ] All tests pass
- [ ] New functionality includes tests
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] No merge conflicts with main branch

## 🎯 Areas for Contribution

### High Priority
- Performance optimizations
- Additional data format support
- Enhanced search functionality
- Better error handling

### Medium Priority
- UI/UX improvements
- Additional export formats
- Plugin system architecture
- Cross-platform compatibility

### Low Priority
- Code refactoring
- Documentation improvements
- Additional themes
- Accessibility features

## 🤔 Questions?

- Open an issue for discussion
- Check existing documentation in `docs/`
- Review the codebase for examples

Thank you for contributing to ShadowHawk Database Browser! 🦅
