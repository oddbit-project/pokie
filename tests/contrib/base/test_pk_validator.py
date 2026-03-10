import pytest

from pokie.contrib.base.validators.pk import DbPrimaryKey, init_validators


class TestDbPrimaryKey:
    def test_validate_valid_pk(self, pokie_di):
        init_validators(pokie_di)
        rule = DbPrimaryKey()
        result, msg = rule.validate("FIXTURE", options=["customers", "customer_id"])
        assert result is True

    def test_validate_invalid_pk(self, pokie_di):
        init_validators(pokie_di)
        rule = DbPrimaryKey()
        result, msg = rule.validate("NONEXISTENT_KEY_XYZ", options=["customers", "customer_id"])
        assert result is False

    def test_missing_table_name(self, pokie_di):
        init_validators(pokie_di)
        rule = DbPrimaryKey()
        with pytest.raises(RuntimeError, match="missing table name"):
            rule.validate("value", options=[])

    def test_invalid_table_format(self, pokie_di):
        init_validators(pokie_di)
        rule = DbPrimaryKey()
        with pytest.raises(ValueError, match="invalid table name"):
            rule.validate("value", options=["a.b.c"])

    def test_di_not_initialized(self):
        import pokie.contrib.base.validators.pk as pk_module

        old_di = pk_module._di
        try:
            pk_module._di = None
            rule = DbPrimaryKey()
            with pytest.raises(RuntimeError, match="di not initialized"):
                rule.validate("value", options=["customers"])
        finally:
            pk_module._di = old_di

    def test_with_schema_prefix(self, pokie_di):
        init_validators(pokie_di)
        rule = DbPrimaryKey()
        result, msg = rule.validate("FIXTURE", options=["public.customers", "customer_id"])
        assert result is True
