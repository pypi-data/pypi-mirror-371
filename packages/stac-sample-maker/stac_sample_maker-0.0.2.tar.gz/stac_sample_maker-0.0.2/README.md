# STAC Sample Maker

[![Tests](https://github.com/developmentseed/stac-sample-maker/workflows/Tests/badge.svg)](https://github.com/developmentseed/stac-sample-maker/actions)
[![PyPI version](https://badge.fury.io/py/stac-sample-maker.svg)](https://badge.fury.io/py/stac-sample-maker)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Generate synthetic [STAC (SpatioTemporal Asset Catalog)](https://stacspec.org/) items with realistic metadata for testing, development, and demonstration purposes.

## Features

- 🌍 **Complete STAC compliance**: Generates valid STAC v1.1.0 items
- 🔧 **All stable extensions**: Supports EO, File, Projection, View, SAR, Scientific, and Landsat extensions
- 📝 **Template-based generation**: Create items matching existing STAC item structures
- ✅ **Schema validation**: Optional validation using stac-validator
- 🎯 **Realistic data**: Uses Faker to generate believable synthetic metadata
- 📊 **Common metadata**: Includes STAC common metadata fields (license, providers, etc.)
- 🔄 **Flexible output**: NDJSON format with stdout or file output
- 🎲 **Reproducible**: Seed support for consistent outputs

## Installation

### Basic Installation

```bash
pip install stac-sample-maker
```

### With Validation Support

```bash
pip install stac-sample-maker[validation]
```

### Development Installation

```bash
git clone https://github.com/developmentseed/stac-sample-maker.git
cd stac-sample-maker
pip install -e ".[dev,validation]"
```

## Quick Start

### Command Line Usage

Generate 5 synthetic STAC items:

```bash
stac-sample-maker --num-items 5
```

Generate items with validation:

```bash
stac-sample-maker --num-items 3 --validate
```

Generate items from a template:

```bash
stac-sample-maker --template my-stac-item.json --num-items 10
```

Save to a file:

```bash
stac-sample-maker --num-items 5 --output samples.ndjson
```

### Library Usage

```python
from stac_sample_maker import generate_stac_items

# Generate basic items
items = generate_stac_items(num_items=5)

# Generate with specific parameters
items = generate_stac_items(
    num_items=10,
    start_date="2020-01-01T00:00:00Z",
    end_date="2023-12-31T23:59:59Z",
    bbox=[-122.5, 37.7, -122.3, 37.8],  # San Francisco area
    seed=42,  # For reproducible results
    validate=True  # Requires stac-validator
)

# Generate from template
from stac_sample_maker import generate_stac_items_from_template

items = generate_stac_items_from_template(
    template_path="example-item.json",
    num_items=5
)
```

## Command Line Interface

```bash
stac-sample-maker [OPTIONS]
```

### Options

| Option | Description | Default |
|--------|-------------|---------|
| `--num-items N` | Number of STAC items to generate | 1 |
| `--template PATH` | Path to template STAC item JSON file | None |
| `--output PATH` | Output file path (NDJSON format) | stdout |
| `--start DATE` | Start of datetime range (ISO 8601) | None |
| `--end DATE` | End of datetime range (ISO 8601) | None |
| `--interval-percent FLOAT` | Fraction of items using intervals (0-1) | 0.2 |
| `--bbox MINX MINY MAXX MAXY` | Bounding box for geometry | None |
| `--seed INT` | Random seed for reproducibility | None |
| `--validate` | Validate items against STAC schema | False |

### Examples

```bash
# Generate 100 items for 2023 with 50% using time intervals
stac-sample-maker --num-items 100 \
  --start "2023-01-01T00:00:00Z" \
  --end "2023-12-31T23:59:59Z" \
  --interval-percent 0.5

# Generate items within a bounding box (San Francisco)
stac-sample-maker --num-items 20 \
  --bbox -122.5 37.7 -122.3 37.8

# Generate reproducible items with validation
stac-sample-maker --num-items 10 \
  --seed 42 \
  --validate \
  --output validated-items.ndjson
```

## Library API

### Core Functions

#### `generate_stac_items()`

Generate synthetic STAC items with all extensions.

```python
def generate_stac_items(
    num_items: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    interval_percent: float = 0.2,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    seed: Optional[int] = None,
    extensions: Optional[List[str]] = None,
    validate: bool = False,
) -> List[dict]:
```

#### `generate_stac_items_from_template()`

Generate STAC items matching a template structure.

```python
def generate_stac_items_from_template(
    template_path: str,
    num_items: int,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    bbox: Optional[Tuple[float, float, float, float]] = None,
    seed: Optional[int] = None,
    validate: bool = False,
) -> List[Dict[str, Any]]:
```

#### `validate_stac_item()`

Validate a STAC item against JSON schema.

```python
def validate_stac_item(
    item: Dict[str, Any],
    strict: bool = True
) -> bool:
```

### Supported Extensions

- **EO (Electro-Optical)**: Cloud cover, snow cover, spectral bands
- **File**: File size, checksums, header information
- **Projection**: EPSG codes, transforms, shapes, bounding boxes
- **View**: Viewing angles, sun position, off-nadir angles
- **SAR**: Radar-specific metadata (frequency, polarization, etc.)
- **Scientific**: DOI citations, publications
- **Landsat**: Landsat-specific metadata (WRS path/row, etc.)

### Template Mode

Template mode analyzes an existing STAC item and generates new items with the same structure:

1. **Extensions**: Matches the exact extensions used
2. **Properties**: Generates new values for the same property fields
3. **Assets**: Creates assets with the same keys and structure
4. **Temporal**: Preserves instant vs. interval temporal patterns

Example template workflow:

```python
# Save one generated item as a template
items = generate_stac_items(num_items=1)
with open("template.json", "w") as f:
    json.dump(items[0], f)

# Generate more items matching the template
similar_items = generate_stac_items_from_template(
    template_path="template.json",
    num_items=100
)
```

## STAC Compliance

Generated items are fully compliant with:

- **STAC Specification v1.1.0**
- **All stable STAC extensions**
- **STAC Common Metadata** (license, providers, platform, etc.)
- **GeoJSON standards** for geometry
- **ISO 8601** for datetime formatting

## Development

### Setup

```bash
git clone https://github.com/developmentseed/stac-sample-maker.git
cd stac-sample-maker
pip install -e ".[dev,validation]"
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=stac_sample_maker --cov-report=html

# Run specific tests
pytest tests/test_generator.py -v
```

### Code Quality

```bash
# Format code
ruff format

# Lint code
ruff check

# Type checking
mypy stac_sample_maker
```

### Pre-commit Hooks

The project uses pre-commit hooks for code quality:

```bash
pre-commit run --all-files
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linting (`pytest && ruff check && mypy stac_sample_maker`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [STAC Specification](https://stacspec.org/) for the standard
- [Faker](https://faker.readthedocs.io/) for synthetic data generation
- [stac-validator](https://github.com/stac-utils/stac-validator) for validation support

## Related Projects

- [PySTAC](https://pystac.readthedocs.io/) - Python library for working with STAC
- [STAC Validator](https://github.com/stac-utils/stac-validator) - Validation tools
- [STAC Browser](https://github.com/radiantearth/stac-browser) - Browse STAC catalogs
- [STAC Index](https://stacindex.org/) - Discover STAC resources
