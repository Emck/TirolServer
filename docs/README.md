# Generate Documentation

## Requirements

Install the documentation dependencies with:

```bash
uv sync

or

pip install "tirolserver[docs]"
```

This provides griffe2md and griffe supporting plugins.

## Generate markdown Documentation

```bash
gendocs

or

pip: python scripts/gendocs.py
```

The Generate Documentation into the `docs/content/` directory.

