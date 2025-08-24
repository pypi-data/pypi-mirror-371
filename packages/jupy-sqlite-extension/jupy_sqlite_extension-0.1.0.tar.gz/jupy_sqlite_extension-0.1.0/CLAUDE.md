# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a JupyterLab extension for SQLite execution based on cell metadata without magic commands. It consists of:
- **Frontend**: TypeScript/React extension for JupyterLab (`src/` directory)
- **Backend**: Python server extension (`jupy_sqlite_extension/` directory)
- **Tests**: Jest tests for frontend, Pytest for backend, Playwright for integration

## Development Commands

### Setup and Installation
```bash
# Development install
pip install -e ".[test]"
jupyter labextension develop . --overwrite
jupyter server extension enable jupy_sqlite_extension

# Install dependencies
jlpm
```

### Build Commands
```bash
# Development build (with source maps)
jlpm build

# Production build
jlpm build:prod

# Clean builds
jlpm clean:all
```

### Development Workflow
```bash
# Watch mode (auto-rebuild on changes)
jlpm watch

# Run JupyterLab (in separate terminal)
jupyter lab
```

### Testing
```bash
# Frontend tests (Jest)
jlpm test

# Backend tests (Pytest)
pytest -vv -r ap --cov jupy_sqlite_extension

# Integration tests (Playwright)
cd ui-tests
jlpm install
jlpm playwright install
jlpm test
```

### Code Quality
```bash
# Lint and format
jlpm lint

# Individual linting
jlpm eslint
jlpm prettier
jlpm stylelint
```

## Architecture

### Frontend Structure
- `src/index.ts`: Main plugin entry point and activation
- `src/handler.ts`: API communication with backend server
- `style/`: CSS styling for the extension

### Backend Structure
- `jupy_sqlite_extension/handlers.py`: Server API handlers
- `jupy_sqlite_extension/__init__.py`: Extension setup and registration
- `jupyter-config/`: Server configuration files

### Key Technologies
- **Frontend**: JupyterLab 4.x, TypeScript, React
- **Backend**: Jupyter Server, Tornado web handlers
- **Build**: jlpm (Yarn), TypeScript compiler, Jupyter builder
- **Testing**: Jest, Pytest, Playwright/Galata

## Code Conventions

### TypeScript/Frontend
- Single quotes for strings
- No trailing commas
- Arrow functions preferred
- Interface names must start with `I` and be PascalCase
- ESLint configuration enforces consistent styling

### Python/Backend
- Standard Python conventions apply
- Async handlers for server endpoints
- Proper authentication decorators required

## Extension Registration

The extension registers both frontend and backend components:
- Frontend plugin ID: `jupy-sqlite-extension:plugin`
- Backend namespace: `jupy-sqlite-extension`
- API endpoints under `/jupy-sqlite-extension/` path

## How the Extension Works

### SQL Cell Execution Flow
1. Extension monitors notebook cells for execution events via `cell.model.stateChanged`
2. When a cell executes, checks for metadata: `sql_cell: true` or `language: 'sql'`
3. Requires `db_file` metadata pointing to SQLite database (relative path only for security)
4. Sends SQL code to backend `/execute-sql` endpoint via POST request
5. Backend uses `rich` library to format SELECT results as ASCII tables with proper alignment
6. Results displayed in cell output area with truncation support (max 25 rows by default)

### Security Features
- Database file paths must be relative (absolute paths rejected)
- File existence validation before execution
- Proper error handling and user feedback
- Tornado authentication decorators on all endpoints

## Important Files and Locations

### Configuration Files
- `pyproject.toml`: Python package configuration with dependencies including `rich>=14.1.0`
- `package.json`: Node.js package with JupyterLab 4.x dependencies and build scripts
- `jupyter-config/server-config/jupy_sqlite_extension.json`: Server extension registration

### Key Source Files
- `src/index.ts:23-89`: Core `executeSQLCell` function handling cell execution logic
- `jupy_sqlite_extension/handlers.py:15-57`: Rich table formatting with `format_table_with_rich`
- `jupy_sqlite_extension/handlers.py:67-145`: SQL execution handler with security checks

### Testing Structure
- `src/__tests__/`: Jest unit tests for frontend
- `jupy_sqlite_extension/tests/`: Pytest tests for backend handlers
- `ui-tests/`: Playwright integration tests using Galata framework