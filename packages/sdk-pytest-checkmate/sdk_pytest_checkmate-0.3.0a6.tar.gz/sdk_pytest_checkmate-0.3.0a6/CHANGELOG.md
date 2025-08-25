# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Add SQL query client with automatic logging
- Add asynchronous HTTP client
- Improve HTML report

## [0.2.0a6] - 2025-08-24

### Added
- `create_http_client()` function for enhanced HTTP testing with automatic request/response logging
- Complete module docstrings for improved code documentation
- Enhanced API documentation in README with HTTP client examples

### Changed
- Updated module `__init__.py` with comprehensive documentation including HTTP client usage examples
- Improved code documentation across all modules with detailed docstrings for classes and functions

### Internal
- Modified test modules to verify functionality

## [0.1.0a4] - 2025-08-19

### Changed
- Revised versioning approach: switched to 0.0.0aN pre-release tag pattern to better reflect early, unstable iteration cadence before first public minor (0.1.0).

### Added
- Display of pytest parametrization values in HTML report: each parametrized test invocation now shows its parameters inline in the test title (e.g. `Test with parametrize [id=2]`), improving traceability when multiple variants run.

### Internal
- No functional logic changes besides exposing collected `callspec.params` in results payload.

## [0.0.3a] - 2025-08-19

### Added
- Dark theme styling for HTML report.
- Theme toggle button (floating) with localStorage persistence across sessions.

## [0.0.2a] - 2025-08-19

### Changed
- HTML report footer simplified: removed display of raw invocation arguments (`Args:`) for a cleaner UI and to avoid leaking local run context.

### Fixed
- Data attachments (`add_data_report`) now stay within the detail card: long / wide JSON or string payloads are wrapped (`white-space: pre-wrap`, `word-break: break-word`) and constrained with a scrollable area (`max-height: 340px`) preventing horizontal page overflow.

## [0.0.1a] - 2025-08-18

### Added
- Initial alpha release of sdk-pytest-checkmate plugin
- **Core Features:**
  - `step(name)` context manager for recording test steps with timing
  - `soft_assert(condition, message)` for non-fatal assertions
  - `add_data_report(data, label)` for attaching arbitrary data to test timeline
- **Pytest Markers:**
  - `@pytest.mark.title(name)` for custom test titles
  - `@pytest.mark.epic(name)` for epic-level test grouping
  - `@pytest.mark.story(name)` for story-level test grouping
- **HTML Reporting:**
  - Rich interactive HTML reports with timeline view
  - Expandable/collapsible epic and story sections
  - Inline data inspection with JSON pretty-printing
  - Status filtering (PASSED, FAILED, SKIPPED, etc.)
  - Step timing and error tracking
  - Soft assertion failure aggregation
- **Command Line Options:**
  - `--report-html[=PATH]` to generate HTML reports
  - `--report-title=TITLE` to customize report title
  - `--report-json=PATH` to export results as JSON
- **Async Support:**
  - Context managers work with both `with` and `async with`
  - Full support for async test functions
- **Type Safety:**
  - Full type hints with `py.typed` marker
  - Compatible with mypy and other type checkers
- **Python Compatibility:**
  - Python 3.10+ support
  - pytest 8.4.1+ compatibility

### Technical Details
- Built with modern Python features (union types, dataclasses)
- Uses pytest's StashKey for test data storage
- Context variables for thread-safe test isolation
- Comprehensive error handling and validation
- JSON serialization for data portability

### Documentation
- Complete README with examples and API reference
- Detailed docstrings for all public functions
- Type annotations for LSP support
- Installation and usage instructions

### Testing
- Comprehensive test suite with 36+ test cases
- Unit tests for all core functionality
- Integration tests for combined features
- Marker functionality tests
- Performance testing for large datasets

### Known Limitations
- Requires Python 3.10+ due to union type syntax
- Large data attachments may impact report size
- HTML reports require modern browsers for full functionality

---

## Version History Legend

- **Added** for new features
- **Changed** for changes in existing functionality  
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

## Links

- [GitHub Repository](https://github.com/o73k51i/sdk-pytest-checkmate)
- [PyPI Package](https://pypi.org/project/sdk-pytest-checkmate/)
- [Issue Tracker](https://github.com/o73k51i/sdk-pytest-checkmate/issues)
