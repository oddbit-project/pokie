import humps
from rick.form import RequestRecord, field

from pokie.codegen.pg import PgTableSpec
from pokie.codegen import RequestGenerator, RecordGenerator

record_tablespec = """
from rick_db import fieldmapper


@fieldmapper(tablename='tablespec_serial', pk='id_tablespec', schema='public')
class TablespecSerialRecord:
    id = 'id_tablespec'
    field_bigint = 'field_bigint'
    field_bigserial = 'field_bigserial'
    field_bit = 'field_bit'
    field_varbit = 'field_varbit'
    field_box = 'field_box'
    field_bytea = 'field_bytea'
    field_char = 'field_char'
    field_varchar = 'field_varchar'
    field_cidr = 'field_cidr'
    field_circle = 'field_circle'
    field_date = 'field_date'
    field_float8 = 'field_float8'
    field_inet = 'field_inet'
    field_int4 = 'field_int4'
    field_interval = 'field_interval'
    field_json = 'field_json'
    field_jsonb = 'field_jsonb'
    field_line = 'field_line'
    field_lseg = 'field_lseg'
    field_macaddr = 'field_macaddr'
    field_macaddr8 = 'field_macaddr8'
    field_money = 'field_money'
    field_numeric = 'field_numeric'
    field_path = 'field_path'
    field_point = 'field_point'
    field_polygon = 'field_polygon'
    field_float4 = 'field_float4'
    field_int2 = 'field_int2'
    field_smallserial = 'field_smallserial'
    field_text = 'field_text'
    field_time = 'field_time'
    field_timetz = 'field_timetz'
    field_timestamp = 'field_timestamp'
    field_timestamptz = 'field_timestamptz'
    field_tsquery = 'field_tsquery'
    field_tsvector = 'field_tsvector'
    field_uuid = 'field_uuid'
    field_xml = 'field_xml'

"""

record_tablespec_camel = """
from rick_db import fieldmapper


@fieldmapper(tablename='tablespec_serial', pk='id_tablespec', schema='public')
class TablespecSerialRecord:
    id = 'id_tablespec'
    fieldBigint = 'field_bigint'
    fieldBigserial = 'field_bigserial'
    fieldBit = 'field_bit'
    fieldVarbit = 'field_varbit'
    fieldBox = 'field_box'
    fieldBytea = 'field_bytea'
    fieldChar = 'field_char'
    fieldVarchar = 'field_varchar'
    fieldCidr = 'field_cidr'
    fieldCircle = 'field_circle'
    fieldDate = 'field_date'
    fieldFloat8 = 'field_float8'
    fieldInet = 'field_inet'
    fieldInt4 = 'field_int4'
    fieldInterval = 'field_interval'
    fieldJson = 'field_json'
    fieldJsonb = 'field_jsonb'
    fieldLine = 'field_line'
    fieldLseg = 'field_lseg'
    fieldMacaddr = 'field_macaddr'
    fieldMacaddr8 = 'field_macaddr8'
    fieldMoney = 'field_money'
    fieldNumeric = 'field_numeric'
    fieldPath = 'field_path'
    fieldPoint = 'field_point'
    fieldPolygon = 'field_polygon'
    fieldFloat4 = 'field_float4'
    fieldInt2 = 'field_int2'
    fieldSmallserial = 'field_smallserial'
    fieldText = 'field_text'
    fieldTime = 'field_time'
    fieldTimetz = 'field_timetz'
    fieldTimestamp = 'field_timestamp'
    fieldTimestamptz = 'field_timestamptz'
    fieldTsquery = 'field_tsquery'
    fieldTsvector = 'field_tsvector'
    fieldUuid = 'field_uuid'
    fieldXml = 'field_xml'

"""

tablespec_serial_names = [
    "id_tablespec",
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


class TestRecordGenerator:
    def test_generate_source(self, pokie_db):
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_serial")
        generator = RecordGenerator()
        # default settings
        src = generator.generate_source(spec)
        assert self._cleanup(src) == self._cleanup(record_tablespec)

        # camelCase
        src = generator.generate_source(spec, camelcase=True)
        assert self._cleanup(src) == self._cleanup(record_tablespec_camel)

    def test_generate_class(self, pokie_db):
        pg_spec = PgTableSpec(pokie_db)
        spec = pg_spec.generate("tablespec_serial")
        generator = RecordGenerator()

        cls = generator.generate_class(spec)
        for name in tablespec_serial_names:
            if name == "id_tablespec":
                assert getattr(cls, "id") == name
            else:
                assert getattr(cls, name) == name

        cls = generator.generate_class(spec, camelcase=True)
        for name in tablespec_serial_names:
            if name == "id_tablespec":
                assert getattr(cls, "id") == name
            else:
                assert getattr(cls, humps.camelize(name)) == name

    def _cleanup(self, s: str):
        for c in ["\n", " "]:
            s = s.replace(c, "")
        return s
