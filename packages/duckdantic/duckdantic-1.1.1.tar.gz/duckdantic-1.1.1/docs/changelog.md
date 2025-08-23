# Changelog

All notable changes to Duckdantic will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Duck API for ergonomic duck typing with Pydantic models
- Method signature checking with `MethodSpec` and `methods_satisfy`
- ABC integration for `isinstance`/`issubclass` support
- Comprehensive trait composition with `union`, `intersect`, and `minus`
- Support for Pydantic v2 field aliases and validation
- Flexible type policies for customizable validation
- High-performance caching for field normalization
- Support for multiple object types (Pydantic, dataclasses, TypedDict, etc.)

### Fixed

- Pydantic AliasChoices extraction for proper alias handling
- Hypothesis test generation to ensure unique field names in traits

### Changed

- Improved Google-style docstrings throughout the codebase
- Enhanced error messages and detailed explanations

## [0.1.0] - Initial Release

### Added

- Initial implementation of structural typing for Python
- Basic trait specifications with `TraitSpec` and `FieldSpec`
- Core satisfaction checking with `satisfies` and `explain`
- Field normalization for various Python object types
- Type compatibility policies
- Trait registry for managing collections of traits
