from src.handlers import scout_operations as so


def test_get_profiles_table_fallback(aws_credentials, dynamodb_table):
    so.profiles_table = None
    table = so._get_profiles_table()
    assert getattr(table, "table_name", "") == "kernelworx-profiles-v2-ue1-dev"
