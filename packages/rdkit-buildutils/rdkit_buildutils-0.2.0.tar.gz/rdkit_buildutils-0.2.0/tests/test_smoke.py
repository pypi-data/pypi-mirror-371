def test_smoke_import():
    import rdkit_buildutils as r
    assert hasattr(r, "__version__")
    assert "build_molecule_final" in r.__all__
