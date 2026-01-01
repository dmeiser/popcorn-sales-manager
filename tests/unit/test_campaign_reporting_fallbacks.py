from src.handlers import campaign_reporting as cr


def test_get_campaigns_table_monkeypatch(monkeypatch):
    dummy = object()
    monkeypatch.setattr(cr, "campaigns_table", dummy)
    assert cr._get_campaigns_table() is dummy


def test_get_campaigns_table_fallback(aws_credentials, dynamodb_table):
    cr.campaigns_table = None
    table = cr._get_campaigns_table()
    assert getattr(table, "table_name", "") == "kernelworx-campaigns-v2-ue1-dev"
