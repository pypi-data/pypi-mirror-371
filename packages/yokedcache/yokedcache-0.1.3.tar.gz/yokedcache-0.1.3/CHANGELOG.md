# Changelog

All notable changes to the YokedCache project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

## [0.1.3] - 2025-08-22

### Added
- CLI module execution support via `python -m yokedcache`
- Full CLI command suite: ping, stats, list, flush, search, export-config, warm
- Comprehensive documentation updates with accurate CLI examples

### Changed
- Improved CLI architecture with proper command registration
- Enhanced GitHub Actions workflow for better CI/CD reliability
- Updated all documentation files for accuracy and completeness

### Fixed
- Redis connection method: changed from `aclose()` to `close()` for proper async connection handling
- CLI command registration issue with async decorators using `functools.wraps`
- CLI parameter conflict with double context passing in async commands
- Black code formatting compliance across all source files
- isort import sorting compliance (added proper blank lines)
- MyPy type checking errors for Redis client methods
- GitHub Actions integration test failures with CLI module execution

### Removed
- Codecov integration temporarily disabled due to rate limiting issues

## [0.1.2] - 2025-08-22

### Added
- Initial project structure and core architecture
- Basic caching functionality with Redis backend
- Automatic cache invalidation on database writes
- Tag-based cache grouping and invalidation
- Pattern-based cache invalidation with wildcards
- Fuzzy search capabilities for cached data
- FastAPI integration with dependency injection
- Database wrapper for automatic query caching
- Comprehensive CLI tool for cache management
- Configuration system with YAML support
- Performance metrics and statistics tracking
- Multiple serialization methods (JSON, Pickle, MessagePack)
- Async/await support throughout the library
- Connection pooling and health checks
- Error handling and graceful fallbacks
- Comprehensive test suite with pytest
- Documentation and usage examples
- Development tooling (pre-commit, Makefile, CI/CD)

## [0.1.0] - 2024-MM-DD

### Added
- Initial release of YokedCache
- Core caching functionality with Redis
- FastAPI integration support
- CLI tool for cache management
- Configuration system
- Basic documentation and examples

[Unreleased]: https://github.com/sirstig/yokedcache/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/sirstig/yokedcache/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/sirstig/yokedcache/compare/v0.1.0...v0.1.2
[0.1.0]: https://github.com/sirstig/yokedcache/releases/tag/v0.1.0
