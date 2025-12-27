from src.handlers import list_unit_catalogs as lul


def test_get_campaigns_table_monkeypatch(monkeypatch):
    dummy = object()
    monkeypatch.setattr(lul, "campaigns_table", dummy)
    assert lul._get_campaigns_table() is dummy


def test_get_catalogs_table_fallback(aws_credentials, dynamodb_table):
    lul.catalogs_table = None
    table = lul._get_catalogs_table()
    assert getattr(table, "table_name", "") == "kernelworx-catalogs-ue1-dev"
