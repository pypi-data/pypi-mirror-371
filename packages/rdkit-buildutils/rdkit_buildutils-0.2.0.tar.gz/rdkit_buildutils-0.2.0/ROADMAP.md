# Roadmap

This file outlines possible future developments and directions for **rdkit_buildutils**.

## Short-term (0.3.x)
- Docs via mkdocs/Sphinx
- First pytest suite + GitHub Actions
- Customizable scoring hooks
- Export helpers for R-group results

## Mid-term (0.4.x – 0.5.x)
- CLI tools (`normalize`, `decompose`)
- Optional DB adapters (SQLAlchemy)
- Additional placeholder notations
- Structured exceptions

## Long-term (> 0.5.x)
- REST API (FastAPI) & visualization
- Integration with HELM tools
- Parallelization & caching

## Guiding principles
- Keep core small and RDKit-only
- Optional extras to avoid heavy deps
- Deterministic, reproducible utilities
- Strong examples and tests
