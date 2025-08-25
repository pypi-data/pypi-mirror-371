# Getting Started

This guide will help you set up and start using the test_project ML template.

## Prerequisites

- Python 3.12+
- Git
- (Optional) CUDA-compatible GPU for accelerated training

## Installation

### 1. Install uv

First, install uv if you haven't already:

```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Clone and Setup Project

```bash
# Clone the repository
git clone https://github.com/appleparan/plsno429
cd plsno429

# Install Python 3.13
uv python install 3.13
uv python pin 3.13

# Install dependencies with CUDA support (Ubuntu/Linux)
uv sync --group dev --group docs --extra cu126

# For CPU-only installation
uv sync --group dev --group docs --extra cpu
```

### 3. Verify Installation

Test the installation by running:

```bash
# Test CLI
test_project-cli hello

# Run tests
uv run pytest
```

## Quick Start

### Running Your First Model

#### 1. NLP Example (BoolQ Dataset)

Train a BERT model for question answering:

```bash
plsno429-cli nlp --max-epochs 3 --accelerator auto
```

#### 2. Vision Example (MNIST Dataset)

Train a CNN for digit classification:

```bash
plsno429-cli vision --max-epochs 5 --accelerator auto
```

#### 3. Tabular Example (Titanic Dataset)

Train a neural network for survival prediction:

```bash
plsno429-cli tabular --max-epochs 10 --accelerator auto
```

### Command Line Options

All training commands support these common options:

- `--max-epochs`: Number of training epochs (default: 10)
- `--accelerator`: Training accelerator ('auto', 'cpu', 'gpu', 'tpu')
- `--devices`: Number of devices to use ('auto', or specific count)
- `--deterministic`: Enable deterministic training (default: True)
- `--random-seed`: Random seed for reproducibility (default: 42)

Example with custom parameters:

```bash
test_project-cli nlp \
    --max-epochs 5 \
    --accelerator gpu \
    --devices 1 \
    --random-seed 123
```

## Development Workflow

### 1. Code Quality

```bash
# Format code
uv run ruff format

# Lint code
uv run ruff check --fix .

# Type checking
uv run mypy src/

# Run pre-commit hooks
uvx pre-commit run --all-files
```

### 2. Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=test_project

# Run specific test file
uv run pytest tests/test_version.py
```

### 3. Documentation

```bash
# Serve documentation locally
uv run mkdocs serve

# Build documentation
uv run mkdocs build
```

## Project Structure

After setup, your project will have this structure:

```plaintext
plsno429/
├── src/plsno429/     # Main source code
├── configs/                    # Hydra configuration files
├── data/                       # Data directories
│   ├── raw/                    # Original data
│   ├── processed/              # Processed data
│   ├── interim/                # Intermediate data
│   └── external/               # External data sources
├── docs/                       # Documentation
├── models/                     # Saved models
├── notebooks/                  # Jupyter notebooks
├── reports/                    # Generated reports
├── tests/                      # Tests
└── pyproject.toml              # Project configuration
```

## Configuration

### Hydra Configuration

The project uses Hydra for configuration management. Default configs are in `configs/model_config.toml`.

You can override configurations via CLI:

```bash
# Override config values
plsno429-cli nlp hydra.job.name=my_experiment
```

### Environment Variables

You can set these environment variables:

- `CUDA_VISIBLE_DEVICES`: Specify which GPUs to use
- `HYDRA_FULL_ERROR`: Show full Hydra error traces

## Next Steps

1. **Explore the Code**: Check out the source code in `src/test_project/`
2. **Customize Models**: Modify the model architectures in `nlp.py`, `vision.py`, or `tabular.py`
3. **Add Your Data**: Place your datasets in the appropriate `data/` subdirectories
4. **Create Notebooks**: Use `notebooks/` for exploratory data analysis
5. **Write Tests**: Add tests in the `tests/` directory

## Troubleshooting

### Common Issues

**ImportError: No module named 'test_project'**
```bash
# Ensure you're in the project directory and dependencies are installed
uv sync --group dev
```

**CUDA out of memory**
```bash
# Reduce batch size or use CPU
plsno429-cli nlp --accelerator cpu
```

**Permission denied when running scripts**
```bash
# Make sure scripts are executable
chmod +x scripts/release.sh
```

For more help, check the [API Reference](/reference/plsno429/cli.md) or open an issue on GitHub.
