from rick.form import RequestRecord, field

from pokie.codegen.pg import PgTableSpec
from pokie.codegen import RequestGenerator

tablespec_serial_record = """
from rick.form import RequestRecord, field

class TablespecSerialRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'field_bigint': field(validators='numeric', bind='field_bigint'),
        'field_bigserial': field(validators='numeric', bind='field_bigserial'),
        'field_bit': field(validators='', bind='field_bit'),
        'field_varbit': field(validators='', bind='field_varbit'),
        'field_box': field(validators='', bind='field_box'),
        'field_bytea': field(validators='', bind='field_bytea'),
        'field_char': field(validators='maxlen:10', bind='field_char'),
        'field_varchar': field(validators='maxlen:10', bind='field_varchar'),
        'field_cidr': field(validators='', bind='field_cidr'),
        'field_circle': field(validators='', bind='field_circle'),
        'field_date': field(validators='iso8601', bind='field_date'),
        'field_float8': field(validators='', bind='field_float8'),
        'field_inet': field(validators='', bind='field_inet'),
        'field_int4': field(validators='numeric', bind='field_int4'),
        'field_interval': field(validators='', bind='field_interval'),
        'field_json': field(validators='', bind='field_json'),
        'field_jsonb': field(validators='', bind='field_jsonb'),
        'field_line': field(validators='', bind='field_line'),
        'field_lseg': field(validators='', bind='field_lseg'),
        'field_macaddr': field(validators='', bind='field_macaddr'),
        'field_macaddr8': field(validators='', bind='field_macaddr8'),
        'field_money': field(validators='', bind='field_money'),
        'field_numeric': field(validators='decimal', bind='field_numeric'),
        'field_path': field(validators='', bind='field_path'),
        'field_point': field(validators='', bind='field_point'),
        'field_polygon': field(validators='', bind='field_polygon'),
        'field_float4': field(validators='', bind='field_float4'),
        'field_int2': field(validators='numeric', bind='field_int2'),
        'field_smallserial': field(validators='numeric', bind='field_smallserial'),
        'field_text': field(validators='', bind='field_text'),
        'field_time': field(validators='', bind='field_time'),
        'field_timetz': field(validators='', bind='field_timetz'),
        'field_timestamp': field(validators='iso8601', bind='field_timestamp'),
        'field_timestamptz': field(validators='iso8601', bind='field_timestamptz'),
        'field_tsquery': field(validators='', bind='field_tsquery'),
        'field_tsvector': field(validators='', bind='field_tsvector'),
        'field_uuid': field(validators='', bind='field_uuid'),
        'field_xml': field(validators='', bind='field_xml'),   
    }
"""

tablespec_serial_record_camel = """
from rick.form import RequestRecord, field

class TablespecSerialRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'fieldBigint': field(validators='numeric', bind='field_bigint'),
        'fieldBigserial': field(validators='numeric', bind='field_bigserial'),
        'fieldBit': field(validators='', bind='field_bit'),
        'fieldVarbit': field(validators='', bind='field_varbit'),
        'fieldBox': field(validators='', bind='field_box'),
        'fieldBytea': field(validators='', bind='field_bytea'),
        'fieldChar': field(validators='maxlen:10', bind='field_char'),
        'fieldVarchar': field(validators='maxlen:10', bind='field_varchar'),
        'fieldCidr': field(validators='', bind='field_cidr'),
        'fieldCircle': field(validators='', bind='field_circle'),
        'fieldDate': field(validators='iso8601', bind='field_date'),
        'fieldFloat8': field(validators='', bind='field_float8'),
        'fieldInet': field(validators='', bind='field_inet'),
        'fieldInt4': field(validators='numeric', bind='field_int4'),
        'fieldInterval': field(validators='', bind='field_interval'),
        'fieldJson': field(validators='', bind='field_json'),
        'fieldJsonb': field(validators='', bind='field_jsonb'),
        'fieldLine': field(validators='', bind='field_line'),
        'fieldLseg': field(validators='', bind='field_lseg'),
        'fieldMacaddr': field(validators='', bind='field_macaddr'),
        'fieldMacaddr8': field(validators='', bind='field_macaddr8'),
        'fieldMoney': field(validators='', bind='field_money'),
        'fieldNumeric': field(validators='decimal', bind='field_numeric'),
        'fieldPath': field(validators='', bind='field_path'),
        'fieldPoint': field(validators='', bind='field_point'),
        'fieldPolygon': field(validators='', bind='field_polygon'),
        'fieldFloat4': field(validators='', bind='field_float4'),
        'fieldInt2': field(validators='numeric', bind='field_int2'),
        'fieldSmallserial': field(validators='numeric', bind='field_smallserial'),
        'fieldText': field(validators='', bind='field_text'),
        'fieldTime': field(validators='', bind='field_time'),
        'fieldTimetz': field(validators='', bind='field_timetz'),
        'fieldTimestamp': field(validators='iso8601', bind='field_timestamp'),
        'fieldTimestamptz': field(validators='iso8601', bind='field_timestamptz'),
        'fieldTsquery': field(validators='', bind='field_tsquery'),
        'fieldTsvector': field(validators='', bind='field_tsvector'),
        'fieldUuid': field(validators='', bind='field_uuid'),
        'fieldXml': field(validators='', bind='field_xml'),
    }
"""

tablespec_rel_record = """
from rick.form import RequestRecord, field

class TablespecRelRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'fk_tablespec_serial': field(validators='required|numeric|pk:public.tablespec_serial,id_tablespec', bind='fk_tablespec_serial'),
    }
"""

tablespec_rel_record_camel = """
from rick.form import RequestRecord, field

class TablespecRelRequest(RequestRecord):
    fields = {
        'id': field(validators='id|numeric', bind='id'),
        'fkTablespecSerial': field(validators='required|numeric|pk:public.tablespec_serial,id_tablespec', bind='fk_tablespec_serial'),
    }
"""
tablespec_serial_names = [
    "id",
    "field_bigint",
    "field_bigserial",
    "field_bit",
    "field_varbit",
    "field_box",
    "field_bytea",
    "field_char",
    "field_varchar",
    "field_cidr",
    "field_circle",
    "field_date",
    "field_float8",
    "field_inet",
    "field_int4",
    "field_interval",
    "field_json",
    "field_jsonb",
    "field_line",
    "field_lseg",
    "field_macaddr",
    "field_macaddr8",
    "field_money",
    "field_numeric",
    "field_path",
    "field_point",
    "field_polygon",
    "field_float4",
    "field_int2",
    "field_smallserial",
    "field_text",
    "field_time",
    "field_timetz",
    "field_timestamp",
    "field_timestamptz",
    "field_tsquery",
    "field_tsvector",
    "field_uuid",
    "field_xml",
]


class TestRequestGenerator:
    def test_generate_source(self, pokie_db):
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_serial")
        generator = RequestGenerator()
        # default settings
        src = generator.generate_source(spec)
        assert self._cleanup(src) == self._cleanup(tablespec_serial_record)

        # camelCase
        src = generator.generate_source(spec, camelcase=True)
        assert self._cleanup(src) == self._cleanup(tablespec_serial_record_camel)

        # default settings -rel
        spec = pg_spec.generate("tablespec_rel")
        src = generator.generate_source(spec)
        assert self._cleanup(src) == self._cleanup(tablespec_rel_record)

        # camelCase
        src = generator.generate_source(spec, camelcase=True)
        assert self._cleanup(src) == self._cleanup(tablespec_rel_record_camel)

    def test_generate_class(self, pokie_db):
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_serial")
        generator = RequestGenerator()

        cls = generator.generate_class(spec)
        assert issubclass(cls, RequestRecord)
        for name in tablespec_serial_names:
            assert name in cls.fields.keys()

    def test_is_serial_with_serial_pk(self, pokie_db):
        """Serial PK should be detected as serial"""
        pg_spec = PgTableSpec(pokie_db)
        assert pg_spec.is_serial("tablespec_serial", "id_tablespec", "public") is True

    def test_is_serial_with_non_serial_pk(self, pokie_db):
        """Non-serial (varchar) PK should not be detected as serial"""
        pg_spec = PgTableSpec(pokie_db)
        assert pg_spec.is_serial("tablespec_natural_pk", "code", "public") is False

    def test_natural_pk_required(self, pokie_db):
        """Non-auto PK should have 'required' validator"""
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_natural_pk")
        generator = RequestGenerator()

        # find the PK field (code)
        pk_field = [f for f in spec.fields if f.pk][0]
        assert pk_field.name == "code"
        assert not pk_field.auto

        name, validators, target = generator._field(pk_field)
        assert name == "id"
        assert "required" in validators

    def test_default_fields_not_required(self, pokie_db):
        """Fields with DEFAULT values should not be required"""
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_natural_pk")
        generator = RequestGenerator()

        fields_by_name = {f.name: f for f in spec.fields}

        # status has DEFAULT 'active' - should not be required
        name, validators, _ = generator._field(fields_by_name["status"])
        assert "required" not in validators

        # priority has DEFAULT 0 - should not be required
        name, validators, _ = generator._field(fields_by_name["priority"])
        assert "required" not in validators

    def test_not_null_no_default_required(self, pokie_db):
        """NOT NULL field without DEFAULT should be required"""
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_natural_pk")
        generator = RequestGenerator()

        fields_by_name = {f.name: f for f in spec.fields}

        # name is NOT NULL without DEFAULT - should be required
        name, validators, _ = generator._field(fields_by_name["name"])
        assert "required" in validators

    def test_nullable_not_required(self, pokie_db):
        """Nullable field should not be required"""
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_natural_pk")
        generator = RequestGenerator()

        fields_by_name = {f.name: f for f in spec.fields}

        # description is nullable - should not be required
        name, validators, _ = generator._field(fields_by_name["description"])
        assert "required" not in validators

    def _cleanup(self, s: str):
        for c in ["\n", " "]:
            s = s.replace(c, "")
        return s
