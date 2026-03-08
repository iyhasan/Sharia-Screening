# Release & Deployment

## Local install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
```

## Tests
```bash
pytest
```

## Build distributions
```bash
python -m build
```

## Publish (TestPyPI)
```bash
python -m twine upload --repository testpypi dist/*
```

## Publish (PyPI)
```bash
python -m twine upload dist/*
```

## Versioning
- Bump `version` in `pyproject.toml`.
- Tag the release: `git tag vX.Y.Z`.

## Release checklist
- [ ] Update version in `pyproject.toml`
- [ ] Update README if behavior or CLI changes
- [ ] Run tests (`pytest`)
- [ ] Build sdist/wheel (`python -m build`)
- [ ] Verify artifacts in `dist/`
- [ ] Upload to TestPyPI
- [ ] Smoke-test install from TestPyPI
- [ ] Upload to PyPI
