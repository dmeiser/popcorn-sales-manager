from src.handlers import scout_operations as so


def test_get_profiles_table_monkeypatch(monkeypatch):
    dummy = object()
    monkeypatch.setattr(so, "profiles_table", dummy)
    assert so._get_profiles_table() is dummy
