# rdkit_buildutils

Utilities built on top of [RDKit](https://www.rdkit.org/) for constructing, normalizing and decomposing molecules with placeholder substitution.  

The package is designed to support workflows involving **monomers**, **R-group decomposition**, and **scaffold normalization**, keeping functions **general-purpose** and lightweight.  

> ⚠️ Developed in a personal context for scientific support. Not affiliated with RDKit or any specific organization.

---

## ✨ Features

### Core utilities (`rdkit_buildutils/core.py`)
- `convert_r_to_atom_map(smiles_r)`: Convert placeholders like `[R1]`, `[R2]` into RDKit-compatible `[*:1]`, `[*:2]`.
- `build_molecule_final(base_smiles, **substituents)`: Replace placeholders in a scaffold SMILES with substituents (`r1="CC"`, `r2="O"`, etc.).

### R-group decomposition (`rdkit_buildutils/rgroup_core.py`)
- `to_core(smiles_with_R)`: Convert scaffold with `[Rk]` into RDKit `Mol` with `[*:k]`.
- `normalize_rgroup_smiles(mol)`: Normalize R-group fragment SMILES (removes atom map numbers, canonicalizes).
- `to_peptidic_scaffold(asis_scaffold)`: Convert peptide-like scaffolds `[R]-N` / `C(=O)-[R]` into peptidic convention (amide/ester aware).
- `anchored_smiles(raw)`: Convert `-OC`, `-C` into canonical `*OC`, `*C` notation.
- `build_code_map(rgroups)`: Build code → anchored SMILES dictionary for substituent matching.
- `decompose_with_cores(mol, core_entries, code_map)`: Run RDKit RGroupDecomposition on multiple possible cores, choose the best by scoring.
- `decompose_for_monomer(mol, monomer_name, monomers_as_is, code_map, alt_cores=None)`: Convenience wrapper using as-is/peptidic/alt cores.

### Scaffold normalization (`rdkit_buildutils/scaffold_normalize.py`)
- `canonical_ranks(mol)`: Robust fallback for atom canonical ranks.
- `r_to_atommap(smiles_r)`: Convert `[R1]..` → `[*:1]..` to `Mol`.
- `relabel_dummies_canonically(mol)`: Deterministic renumbering of dummy atoms `[*:k]` → `[*:1..m]`.
- `normalize_scaffold_chiral(smiles_with_R, relabel_R=True)`: Canonicalize scaffolds **preserving stereochemistry** (D/L).

### Duplicate detection with pandas (optional)
- `find_duplicate_monomers_chiral_df(df, ...)` in `duplicates_pandas.py` to detect duplicates across monomer libraries.

---

## 📦 Installation

Basic:
```bash
pip install rdkit_buildutils
```

With pandas helpers:
```bash
pip install rdkit_buildutils[pandas]
```

With DB extras (for your own adapters):
```bash
pip install rdkit_buildutils[db]
```

---

## 🔬 Examples

### Build molecule with substituents
```python
from rdkit_buildutils import convert_r_to_atom_map, build_molecule_final
from rdkit import Chem

scaffold = "[R1]NCC(=O)[R2]"
core = convert_r_to_atom_map(scaffold)  # -> [*:1]NCC(=O)[*:2]

mol = build_molecule_final(core, r1="C", r2="OC")
print(Chem.MolToSmiles(mol))
```

### Decompose a protected amino acid
```python
from rdkit import Chem
from rdkit_buildutils import build_code_map, decompose_for_monomer

MONOMERS = {"Ser": "[R1]N[C@H]([R3])C([R2])=O"}
RGROUPS = {"BOC": "-C(=O)OC(C)(C)C", "OME": "-OC", "CH2OH": "-CO"}

code_map = build_code_map(RGROUPS)
mol = Chem.MolFromSmiles("CC(C)(C)OC(=O)N[C@H](CO)C(=O)OC")
out = decompose_for_monomer(mol, "Ser", MONOMERS, code_map)
print(out["core_used"], out["core_origin"], out["score"])
```

### Normalize scaffolds with stereochemistry
```python
from rdkit_buildutils import normalize_scaffold_chiral

print(normalize_scaffold_chiral("[R1]N[C@H](CO)C([R2])=O", relabel_R=True))
```

### Find duplicates in a pandas DataFrame
```python
import pandas as pd
from rdkit_buildutils.duplicates_pandas import find_duplicate_monomers_chiral_df

df = pd.DataFrame([
    {"id":1,"symbol":"L-Ser","scaffold_smiles":"[R1]N[C@H](CO)C([R2])=O","author":"Alice"},
    {"id":2,"symbol":"L-Ser_alt","scaffold_smiles":"[R1]N[C@H](CO)C([R2])=O","author":"Bob"},
    {"id":3,"symbol":"D-Ser","scaffold_smiles":"[R1]N[C@@H](CO)C([R2])=O","author":"Carol"},
])
dup = find_duplicate_monomers_chiral_df(df, relabel_R=True)
print(dup)
```

---

## 🧩 Optional extras
- `[pandas]`: DataFrame adapters (duplicate search).
- `[db]`: Optional dependencies if you want to build database adapters in your project.

---

## 📖 Documentation
Docstrings + README. Roadmap for mkdocs/Sphinx in `ROADMAP.md`.

## ✅ License
MIT © 2025 Fabio Nelli
