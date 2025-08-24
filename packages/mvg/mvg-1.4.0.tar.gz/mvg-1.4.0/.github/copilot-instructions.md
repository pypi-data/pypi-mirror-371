# AI Agent Instructions for MVG API Project

This document provides essential guidance for AI agents working with the MVG API codebase.

## Project Overview

This is a Python package providing a clean interface to Munich's public transport (MVG) timetable information. Key features:
- Async/sync API for station lookup and departure information
- Strongly typed with Python type hints
- Designed for integration with Home Assistant and other applications

## Core Architecture

The project is structured around the `MvgApi` class in `src/mvg/mvgapi.py`:
- Uses Enum classes for API configuration (`Base`, `Endpoint`, `TransportType`)
- Provides both sync and async methods for all operations
- Main data flows: Station Lookup -> API Instance Creation -> Departure Queries

## Development Environment

Required setup:
```python
# Install dev dependencies
pip install .[dev]
```

## Key Developer Workflows

1. Running Tests:
   - Use `tox` to run tests across Python versions
   - Tests are in `tests/test_demo.py`

2. Building Documentation:
   - Docs source in `docs/source/`
   - Build with `sphinx-build docs/source/ docs/build`

3. Building Package:
   - Uses `hatchling` build system
   - Build with `python -m build`

## Project Conventions

1. API Response Formats:
   - Station results are dicts with `id`, `name`, `place`, `latitude`, `longitude`
   - Departure results are lists of dicts with `time`, `planned`, `line`, `destination`, `type`, `icon`

2. Transport Types:
   - Use `TransportType` enum for filtering (e.g. `TransportType.UBAHN`, `TransportType.SBAHN`)
   - Each type has associated display name and MDI icon

3. Error Handling:
   - Methods like `station()` return `None` if no match found
   - API errors raise exceptions that should be handled by client code

## Integration Points

1. External Dependencies:
   - `aiohttp` for async HTTP requests
   - `furl` for URL manipulation
   - Compatible with Python 3.8+

2. Key Files for Extension:
   - Add new transport types in `TransportType` enum
   - API endpoints configured in `Endpoint` enum
   - Tests show usage patterns in `tests/test_demo.py`

## Project Overview
- This is an unofficial Python interface to Munich's public transport (MVG) timetable information
- Provides clean, async-capable access to station, line and departure data via MVG's JSON API
- Key use cases: Integration with Home Assistant and other concurrent code projects
- Private, non-commercial use only (see MVG usage restrictions)

## Core Architecture

### Key Components
- `MvgApi` class (`src/mvg/mvgapi.py`) - Main interface for all API interactions
- Base URLs defined in `Base` enum:
  - FIB API: `https://www.mvg.de/api/bgw-pt/v3` (primary API)
  - ZDM API: `www.mvg.de/.rest/zdm` (supplementary data)
- `TransportType` enum defines supported transport modes with icons

### Data Flow
1. Station lookup via `station()` or `nearby()` methods
2. Create `MvgApi` instance with station ID
3. Fetch departures with optional filtering

## Development Workflow

### Setup & Testing
```bash
pip install .[dev]  # Install with dev dependencies
python -m pytest    # Run tests
```

### Common Tasks
- Build package: `python -m build`  
- Build docs: `sphinx-build docs/source/ docs/build`
- Code quality: Project uses flake8, black, mypy, pylint

### Key Patterns
- Always validate station IDs with `valid_station_id()`
- Use asynchronous methods for concurrent operations
- Return types follow standard formats (see README examples)

## Project-Specific Conventions
- Station IDs must match VDV 432 format: `de:xxxxx:xxx`
- Transport types are strictly enumerated in `TransportType`
- Default departure limit: 10 items (max 100)
- Prefer async methods over synchronous ones for better performance

## Integration Points
- Primary dependencies: aiohttp (~3.8), furl (~2.1)
- Python 3.7+ required
- Designed for Home Assistant integration
- API responses match www.mvg.de format for compatibility
