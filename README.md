# Neuro-iX Tools  
Common Tools for the Neuro-iX Lab

## Getting Started

### Installation

You will need an environment with at least **Python 3.11**, then run:

```bash
pip install neuro-ix-tools
```

Alternatively, you can clone the repository and use:

```bash
python cli.py
```

instead of `neuro-ix`.

### Setup

If you are using the package, simply run:

```bash
neuro-ix init
```

This provides sensible defaults for Narval. The configuration file is stored in your `.config` folder.

If you are using the repository directly, we recommend using a local `.env` file. A template is available at `.example.env`.

### Usage

Inside this environment, you have access to the `neuro-ix` command, which currently exposes one main tool.

#### FreeSurfer `recon-all` on SLURM Cluster

We provide a pipeline that simplifies the usage of FreeSurfer on the Narval SLURM cluster. The main command is:

```bash
neuro-ix freesurfer recon-all
```

This allows users to process all subjects in either a BIDS or CAPS (Clinica) dataset with FreeSurfer, using one SLURM job per subject.

##### Arguments:

- `--bids-dataset`: Path to the root of a BIDS-compliant dataset
- `--clinica-dataset`: Path to the root of a Clinica-compliant dataset (CAPS)
- `--cortical-stats`: Flag to store only FreeSurfer's stats files
- `--start-from`: Used when there are more than 1000 subjects due to Narval’s job limit. Allows the user to resume processing from a specific subject index.

##### Example:

```bash
neuro-ix freesurfer recon-all --bids-dataset /path/to/dataset
```

If your dataset includes more than 1000 subjects (e.g., 1500), once the first batch is done, run:

```bash
neuro-ix freesurfer recon-all --bids-dataset /path/to/dataset --start-from 1000
```

### Library

As a library, the `neuro_ix` package exposes:

- Classes to interact with and query BIDS and CAPS datasets for T1-weighted MRIs
- Extendable command classes

## Contributing

### Setup

Once the repository is cloned, install the development dependencies with:

```bash
pip install -r dev_requirements.txt
```

### Tests

#### Test Tools

We use:

- `pytest` for unit tests
- `pytest-cov` for coverage reports  
Run tests via:

```bash
pytest --cov
```

- `ruff` for linting and formatting (automatically applied via `pre-commit`)
- Additional tools for code quality: `ssort`, `pydocstyle`, `mypy`, and `pylint`

#### Test Data

All test data are extracted from MR-ART:

> Nárai, Á., Hermann, P., Auer, T. et al. Movement-related artefacts (MR-ART) dataset of matched motion-corrupted and clean structural MRI brain scans. *Sci Data* 9, 630 (2022). https://doi.org/10.1038/s41597-022-01694-8

### Deployment

Build Package using :

```
python -m build
```

And deploy to PyPI with :

```
twine upload dist/*
```
