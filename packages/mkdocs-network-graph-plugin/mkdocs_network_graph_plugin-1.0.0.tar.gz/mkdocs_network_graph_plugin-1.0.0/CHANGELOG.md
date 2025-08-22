# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Interactive graph visualization for MkDocs documentation
- Dual view modes: full-site overview and local page connections
- Seamless integration with Material for MkDocs themes
- Configurable node naming strategies (`title` or `file_name`)
- Debug logging support for development
- Extensive CSS customization via CSS variables
- Responsive design for desktop and mobile devices
- D3.js-powered interactive graph rendering
- Performance-optimized lightweight implementation

### Configuration Options

- `name`: Node naming strategy configuration
- `debug`: Debug logging toggle

### CSS Variables

- `--md-graph-node-color`: Default node color
- `--md-graph-node-color--hover`: Node hover color
- `--md-graph-node-color--current`: Current page node color
- `--md-graph-link-color`: Connection line color
- `--md-graph-text-color`: Node label text color

### Documentation

- Comprehensive documentation site
- Getting started tutorial
- Configuration reference
- Customization guide
- Developer contribution guide

### Development

- Python 3.10+ support
- Material for MkDocs v9.0.0+ compatibility
- Automated testing with pytest
- Code quality tools (ruff, pyright)
- Pre-commit hooks
- GitHub Actions CI/CD pipeline
- Development environment setup with uv
