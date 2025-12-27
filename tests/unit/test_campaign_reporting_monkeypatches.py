from src.handlers import campaign_reporting as cr


def test_profiles_and_orders_monkeypatched(monkeypatch):
    dummy = object()
    monkeypatch.setattr(cr, "profiles_table", dummy)
    monkeypatch.setattr(cr, "orders_table", dummy)

    assert cr._get_profiles_table() is dummy
    assert cr._get_orders_table() is dummy
