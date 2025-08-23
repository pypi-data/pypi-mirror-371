# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.2.0] - 2025-08-21
### Added
- R-group decomposition utilities (`rgroup_core.py`): `to_core`, `normalize_rgroup_smiles`, `to_peptidic_scaffold`, `anchored_smiles`, `build_code_map`, `decompose_with_cores`, `decompose_for_monomer`.
- Scaffold normalization utilities (`scaffold_normalize.py`): `canonical_ranks`, `r_to_atommap`, `relabel_dummies_canonically`, `normalize_scaffold_chiral`.
- Duplicate detection with pandas (`duplicates_pandas.py`): `find_duplicate_monomers_chiral_df`.
- Optional extras: `[pandas]`, `[db]`.

### Changed
- Expanded README with examples.
- Updated `__init__.py` to expose new API.
- Improved packaging metadata in `pyproject.toml`.

### Fixed
- Deterministic relabeling of dummy atoms improves scaffold comparisons.

---

## [0.1.0] - 2025-06-01
### Added
- Initial release with `convert_r_to_atom_map` and `build_molecule_final`.
