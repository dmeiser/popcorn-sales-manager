from src.handlers import campaign_operations as co


def test_module_level_getters_monkeypatched(monkeypatch):
    dummy = object()
    monkeypatch.setattr(co, "campaigns_table", dummy)
    monkeypatch.setattr(co, "shared_campaigns_table", dummy)
    monkeypatch.setattr(co, "shares_table", dummy)
    monkeypatch.setattr(co, "profiles_table", dummy)

    assert co._get_campaigns_table() is dummy
    assert co._get_shared_campaigns_table() is dummy
    assert co._get_shares_table() is dummy
    assert co._get_profiles_table() is dummy


def test_logger_present_after_reload():
    # Access logger attribute to ensure module-level assignment was executed
    assert getattr(co, "logger", None) is not None
