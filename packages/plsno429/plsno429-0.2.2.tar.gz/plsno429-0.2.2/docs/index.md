# plsno429

A tiny Python library that politely says pls no 429 by auto-handling OpenAI rate limits.


## Project Organization

```plaintext
plsno429/
├── LICENSE            <- Open-source license if one is chosen
├── README.md          <- The top-level README for developers using this project.
├── mkdocs.yml         <- mkdocs-material configuration file.
├── pyproject.toml     <- Project configuration file with package metadata for
│                         plsno429 and configuration for tools like ruff
├── uv.lock            <- The lock file for reproducing the production environment, e.g.
│                         generated with `uv sync`
├── data
│   ├── external       <- Data from third party sources.
│   ├── interim        <- Intermediate data that has been transformed.
│   ├── processed      <- The final, canonical data sets for modeling.
│   └── raw            <- The original, immutable data dump.
├── docs               <- A default mkdocs project; see www.mkdocs.org for details
├── models             <- Trained and serialized models, model predictions, or model summaries
├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
│                         the creator's initials, and a short `-` delimited description, e.g.
│                         `1.0-jqp-initial-data-exploration`.
├── references         <- Data dictionaries, manuals, and all other explanatory materials.
├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
│   └── figures        <- Generated graphics and figures to be used in reporting
├── tests              <- Unit test files.
└── src/plsno429   <- Source code for use in this project.
    │
    ├── __init__.py             <- Makes plsno429 a Python module
    │
    └── cli.py                  <- Default CLI program
```

## For Developers

### Whether to use `package`

This determines if the project should be treated as a Python package or a "virtual" project.

A `package` is a fully installable Python module,
while a virtual project is not installable but manages its dependencies in the virtual environment.

If you don't want to use this packaging feature,
you can set `tool.uv.package = false` in the pyproject.toml file.
This tells `uv` to handle your project as a virtual project instead of a package.

### Install Python (3.13)
```shell
uv python install 3.13
```

### Pin Python version
```shell
uv python pin 3.13
```

### Install packages with PyTorch + CUDA 12.6 (Ubuntu)
```shell
uv sync --extra cu126
```

### Install packages without locking environments
```shell
uv sync --frozen
```

### Install dev packages, too
```shell
uv sync --group dev --group docs --extra cu126
```

### Run tests
```shell
uv run pytest
```

### Linting
```shell
uv ruff check --fix .
```

### Formatting
```shell
uv ruff format
```

### Run pre-commit
* Assume that `pre-commit` installed with `uv tool install pre-commit`

```shell
uvx pre-commit run --all-files
```

### Build package
```shell
uv build
```

### Serve Document
```shell
uv run mkdocs serve
```

### Build Document
```shell
uv run mkdocs build
```

### Build Docker Image (from source)

[ref. uv docs](https://docs.astral.sh/uv/guides/integration/docker/#installing-a-project)

```shell
docker build -t TAGNAME -f Dockerfile.source
```

### Build Docker Image (from package)

[ref. uv docs](https://docs.astral.sh/uv/guides/integration/docker/#non-editable-installs)

```shell
docker build -t TAGNAME -f Dockerfile.package
```

### Run Docker Container
```shell
docker run --gpus all -p 8000:8000 my-production-app
```

### Check next version
```shell
uv run git-cliff --bumped-version
```

### Release
Execute scripts
```shell
sh scripts/release.sh
```

What `release.sh` do:

1. Set next version to `BUMPED_VERSION`: This ensures that the `git-cliff --bumped-version` command produces consistent results.

    ```shell
    BUMPED_VERSION=$(uv run git-cliff --bumped-version)
    ```

2. Generate `CHANGELOG.md` and `RELEASE.md`: The script creates or updates the changelog and release notes using the bumped version:

    ```shell
    uv run git-cliff --strip header --tag $BUMPED_VERSION -o CHANGELOG.md
    uv run git-cliff --latest --strip header --tag $BUMPED_VERSION --unreleased -o RELEASE.md
    ```

3. Commit updated `CHANGELOG.md` and `RELEASE.md` then add tags and push: It commits the updated files, creates a tag for the new version, and pushes the changes to the repository:

    ```shell
    git add CHANGELOG.md RELEASE.md
    git commit -am "docs: Add CHANGELOG.md and RELEASE.md to release $BUMPED_VERSION"
    git tag -a v$BUMPED_VERSION -m "Release $BUMPED_VERSION"
    git push origin tag $BUMPED_VERSION
    ```

4. For dry run:

    ```shell
    uv run git-cliff --latest --strip header --tag $(uv run git-cliff --bumped-version) --unreleased
    ```

## References
* [Packaging Python Projects](https://packaging.python.org/tutorials/packaging-projects/)
* [Python Packaging User Guide](https://packaging.python.org/)


** This project template is generated by [copier-modern-ml](https://github.com/appleparan/copier-modern-ml)**
