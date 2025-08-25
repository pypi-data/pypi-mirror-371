# PoI Python SDK Package

This folder contains the PyPI package for the Proof-of-Intent Python SDK.

## Package Structure

```
package/
├── src/                    # Source code
│   └── poi_sdk/          # Main package
├── setup.py               # Package setup script
├── MANIFEST.in            # Package manifest
├── requirements.txt       # Dependencies
├── LICENSE                # MIT License
├── README.md              # This file
└── build_package.py       # Build automation script
```

## Building the Package

### Prerequisites

```bash
pip install setuptools wheel twine
```

### Quick Build

```bash
cd package
python build_package.py
```

### Manual Build

```bash
cd package

# Clean previous builds
rm -rf build dist *.egg-info

# Build source distribution
python setup.py sdist

# Build wheel
python setup.py bdist_wheel

# Check package
twine check dist/*
```

## Package Contents

The package includes:

- **Core SDK**: `PoIReceipt`, `PoIGenerator`, `PoIValidator`, `PoIConfig`
- **CLI Tool**: `poi-cli` command-line interface
- **Type Hints**: Full type annotation support
- **Dependencies**: All required packages with version constraints

## Installation

### From PyPI (when published)

```bash
pip install poi-sdk
```

### From Local Package

```bash
# Install from built wheel
pip install dist/poi_sdk-0.1.0-py3-none-any.whl

# Install in development mode
pip install -e .
```

## Usage

```python
from poi_sdk import PoIGenerator, PoIValidator

# Generate a receipt
generator = PoIGenerator()
receipt = generator.generate_receipt(
    agent_id="my_agent",
    action="data_access",
    target_resource="user_database",
    declared_objective="Fetch user profile"
)

# Validate the receipt
validator = PoIValidator()
is_valid = validator.validate_receipt(receipt)
```

## CLI Usage

```bash
# Generate a receipt
poi-cli generate --agent-id "cli_agent" --action "test" --resource "test" --objective "Testing"

# Validate a receipt
poi-cli validate --receipt receipt.json
```

## Development

For development setup and contribution guidelines, see the main repository's [CONTRIBUTING.md](../CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE) file for details.
