# Contributing to NewsNeuron

We're excited that you're interested in contributing to NewsNeuron! This document outlines the process for contributing to the project and provides guidelines to ensure a smooth collaboration.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it to understand the standards we expect from all contributors.

## Getting Started

### Prerequisites

Before contributing, make sure you have:

- [Node.js](https://nodejs.org/) (v18+)
- [Python](https://python.org/) (v3.9+)
- [Git](https://git-scm.com/)
- [Docker](https://docker.com/) (optional but recommended)

### Areas Where You Can Contribute

- **Frontend Development**: Vue.js components, UI/UX improvements
- **Backend Development**: FastAPI endpoints, AI integration
- **Data Processing**: Entity extraction, embedding generation
- **Database Design**: Schema improvements, query optimization
- **Documentation**: API docs, tutorials, examples
- **Testing**: Unit tests, integration tests, end-to-end tests
- **DevOps**: Deployment, CI/CD, monitoring
- **Design**: UI/UX design, graphics, branding

## Development Setup

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/yourusername/newsneuron.git
   cd newsneuron
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/newsneuron.git
   ```
4. **Set up the development environment** following our [Setup Guide](docs/SETUP.md)

## Making Changes

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 2. Branch Naming Conventions

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Adding or updating tests
- `style/` - Code style changes

### 3. Make Your Changes

- Follow our [coding standards](#coding-standards)
- Write tests for your changes
- Update documentation as needed
- Ensure your code follows the existing patterns

### 4. Test Your Changes

Before submitting, make sure all tests pass:

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test

# Linting
npm run lint  # Frontend
black . && flake8 .  # Backend
```

### 5. Commit Your Changes

Write clear, descriptive commit messages:

```bash
git add .
git commit -m "feat: add entity search functionality

- Implement entity search endpoint
- Add search filters and pagination
- Include comprehensive tests
- Update API documentation

Closes #123"
```

#### Commit Message Format

We follow the [Conventional Commits](https://conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(api): add timeline generation endpoint
fix(frontend): resolve chat input validation issue
docs: update API documentation for search endpoints
test(backend): add unit tests for entity extraction
```

## Submitting Pull Requests

### 1. Push Your Branch

```bash
git push origin feature/your-feature-name
```

### 2. Create a Pull Request

1. Go to the [GitHub repository](https://github.com/original-owner/newsneuron)
2. Click "New Pull Request"
3. Select your branch
4. Fill out the PR template with:
   - Clear description of changes
   - Link to related issues
   - Screenshots (if UI changes)
   - Testing instructions

### 3. PR Requirements

Before your PR can be merged, ensure:

- [ ] All tests pass
- [ ] Code follows style guidelines
- [ ] Documentation is updated
- [ ] No merge conflicts
- [ ] At least one approval from maintainers

### 4. Code Review Process

1. **Automated checks** will run (CI/CD pipeline)
2. **Maintainer review** - we'll review your code and provide feedback
3. **Address feedback** - make requested changes
4. **Final approval** - once approved, your PR will be merged

## Coding Standards

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use [Black](https://black.readthedocs.io/) for code formatting
- Use [flake8](https://flake8.pycqa.org/) for linting
- Write docstrings for all public functions/classes
- Type hints are required for function signatures

```python
from typing import List, Optional

async def process_articles(
    articles: List[Dict[str, Any]], 
    limit: Optional[int] = None
) -> Dict[str, Any]:
    """
    Process a list of articles and extract entities.
    
    Args:
        articles: List of article dictionaries
        limit: Optional limit on number of articles to process
        
    Returns:
        Dictionary containing processed results
    """
    # Implementation here
    pass
```

### JavaScript/Vue.js (Frontend)

- Use **ESLint 9** with flat config format (`eslint.config.js`)
- Follow [Vue.js Style Guide](https://vuejs.org/style-guide/)
- Use **Composition API** with `<script setup>` for all new components
- **TypeScript optional** but encouraged for complex components
- Follow our modern component structure:

```vue
<template>
  <!-- Template here -->
</template>

<script setup>
// Imports
import { ref, computed } from 'vue'

// Props
const props = defineProps({
  // Props definition
})

// Emits
const emit = defineEmits(['event-name'])

// State and logic
// ...
</script>

<style scoped>
/* Component styles */
</style>
```

### General Guidelines

- **Be consistent** with existing code patterns
- **Write readable code** - prefer clarity over cleverness
- **Comment complex logic** - explain the "why", not the "what"
- **Keep functions small** - single responsibility principle
- **Handle errors gracefully** - proper error handling and logging
- **Security first** - validate inputs, sanitize outputs

## Testing Guidelines

### Backend Testing

- **Unit tests** for individual functions/classes
- **Integration tests** for API endpoints
- **Mock external services** (OpenAI, databases in some cases)
- Use `pytest` fixtures for test setup
- Aim for >80% code coverage

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_search_endpoint():
    response = client.post("/api/v1/search/", json={
        "query": "test query",
        "limit": 5
    })
    assert response.status_code == 200
    assert "results" in response.json()
```

### Frontend Testing

- **Unit tests** for components and utilities using **Vitest**
- **Integration tests** for user workflows
- **E2E tests** for critical paths (future implementation)
- **Component testing** with Vue Test Utils
- **Mock API calls** and external dependencies
- **Modern testing** with ESM support

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders correctly', () => {
    const wrapper = mount(MyComponent, {
      props: { title: 'Test Title' }
    })
    expect(wrapper.text()).toContain('Test Title')
  })
})
```

## Documentation

### Code Documentation

- **README files** for each major component (✅ Updated)
- **Inline comments** for complex logic
- **API documentation** using OpenAPI/Swagger (FastAPI auto-generated)
- **Type definitions** and interfaces
- **ESLint configuration** documented in flat config format

### User Documentation

- **Setup guides** for new contributors
- **API documentation** with examples
- **Feature documentation** explaining how to use features
- **Troubleshooting guides** for common issues

### Documentation Standards

- Use clear, concise language
- Include code examples
- Keep documentation up-to-date with code changes
- Use proper markdown formatting

## Community

### Getting Help

- **GitHub Discussions** - for questions and general discussion
- **GitHub Issues** - for bugs and feature requests
- **Discord/Slack** - real-time chat (link in README)

### Reporting Issues

When reporting bugs, include:

1. **Environment details** (OS, Node.js/Python versions)
2. **Steps to reproduce** the issue
3. **Expected vs actual behavior**
4. **Screenshots or logs** if applicable
5. **Minimal reproduction example** if possible

### Suggesting Features

When suggesting new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** you're trying to solve
3. **Propose a solution** with implementation details
4. **Consider backward compatibility**
5. **Be open to discussion** and feedback

## Release Process

1. **Feature freeze** - no new features in release branch
2. **Testing phase** - comprehensive testing of release candidate
3. **Documentation update** - ensure all docs are current
4. **Version bump** - follow semantic versioning
5. **Release notes** - detailed changelog
6. **Deployment** - automated deployment to production

## Recognition

Contributors will be recognized in:

- **Contributors list** in README
- **Release notes** for significant contributions
- **Annual contributor report**

## Questions?

If you have questions about contributing, feel free to:

- Open a GitHub Discussion
- Join our community chat
- Reach out to maintainers directly

Thank you for contributing to NewsNeuron! 🚀
