# STFU - Terraform CLI Wrapper

A beautiful Terraform CLI wrapper with enhanced UI capabilities.

## Overview

STFU (Simple Terraform Frontend Utility) is a Python CLI tool that acts as a drop-in replacement for the `terraform` command while providing enhanced visualization and user experience features. It wraps the standard Terraform CLI and processes its output to display beautiful, interactive interfaces.

## Features

- **Drop-in Replacement**: Use `stfu` or `tf` instead of `terraform` - all commands pass through seamlessly
- **Enhanced UI**: Beautiful output formatting and visualization (UI components designed in Figma)
- **Extensible Architecture**: Easy to add new UI components and modify existing ones
- **Command Intelligence**: Special handling for different Terraform commands (apply, destroy, plan, etc.)
- **Output Processing**: Parses and enhances Terraform output for better readability

## Installation

```bash
pip install stfu-terraform
```

## Usage

Use `stfu` exactly like you would use `terraform`:

```bash
# Initialize a Terraform project
stfu init

# Plan changes
stfu plan

# Apply changes
stfu apply

# Destroy infrastructure
stfu destroy

# Show current state
stfu show
```

## Development

### Setup

```bash
# Clone the repository
git clone <repository-url>
cd stfu

# Install in development mode
pip install -e .[dev]
```

### Testing

```bash
pytest
```

### Code Formatting

```bash
black .
flake8 .
mypy .
```

## Architecture

- `stfu/cli.py` - Main CLI entry point
- `stfu/terraform.py` - Terraform command wrapper and execution
- `stfu/parser.py` - Output parsing and processing
- `stfu/ui/` - UI components and rendering
- `stfu/config.py` - Configuration management

## License

MIT License - see LICENSE file for details.
