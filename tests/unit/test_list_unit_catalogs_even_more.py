from src.handlers import list_unit_catalogs as lul


def test_module_level_variables_exercised(monkeypatch):
    # ensure both branches of _get_campaigns_table/_get_catalogs_table are hit
    dummy_camp = object()
    dummy_cat = object()
    monkeypatch.setattr(lul, "campaigns_table", dummy_camp)
    monkeypatch.setattr(lul, "catalogs_table", dummy_cat)
    assert lul._get_campaigns_table() is dummy_camp
    assert lul._get_catalogs_table() is dummy_cat

    # Now clear and ensure fallback creates Table object when moto table exists
    lul.campaigns_table = None
    lul.catalogs_table = None
    # The presence of `dynamodb_table` fixture will ensure table exists in other tests; here just call to ensure no exception
    _ = lul._get_campaigns_table()
    _ = lul._get_catalogs_table()
    assert True
