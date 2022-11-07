from rick.util.string import snake_to_camel, snake_to_pascal

from pokie.codegen.spec import FieldSpec, TableSpec
from pokie.codegen.textfile import TextBuffer


class RequestGenerator:
    # default validators for misc data types
    validators = {
        'int2': ['numeric'],
        'int4': ['numeric'],
        'int8': ['numeric'],
        'numeric': ['decimal'],
        'bool': ['bool'],
        'timestamptz': ['iso8601'],
        'timestamp': ['iso8601'],
        'date': ['iso8601'],
    }

    def _field(self, f: FieldSpec, camelcase=False, db_camelcase=False) -> tuple:
        """
        Generate a RequestRecord field definition
        :param f:
        :param camelcase:
        :param db_camelcase:
        :return: touple with (name, validators, bind_name)
        """
        validators = []
        if not f.pk:
            name = f.name if camelcase is False else snake_to_camel(f.name)
            target = f.name if db_camelcase is False else snake_to_camel(f.name)

            if not f.nullable:
                validators.append('required')
        else:
            # primary key name is always id
            # if it is an auto number, validate as id
            name = 'id'
            if f.auto:
                validators.append('id')
            target = f.name if db_camelcase is False else snake_to_camel(f.name)

        # add predefined validators for data types
        if f.dtype in self.validators.keys():
            for v in self.validators[f.dtype]:
                validators.append(v)

        # add maxlen if defined in spec
        if 'maxlen' in f.dtype_spec.keys():
            validators.append('maxlen:{}'.format(str(f.dtype_spec['maxlen'])))

        # add foreign key lookup
        if f.fk:
            validators.append('pk:{}.{},{}'.format(f.fk_schema, f.fk_table, f.fk_column))

        return name, validators, target

    def _gen_field_src(self, f: FieldSpec, camelcase=False, db_camelcase=False) -> str:
        """
        Assemble a field definition source code line
        :param f:
        :param camelcase:
        :param db_camelcase:
        :return: str
        """
        name, validators, target = self._field(f, camelcase, db_camelcase)
        validators = "|".join(validators)
        return "'{name}': field(validators='{validators}', bind='{bind}')," \
            .format(name=name, validators=validators, bind=target)

    def gen_source(self, spec: TableSpec, camelcase=False, db_camelcase=False, gen: TextBuffer = None):
        """
        Generate a Rick RequestRecord source file

        :param spec: Table spec
        :param camelcase: if True, attributes will be camelCased
        :param db_camelcase: if True, db record attributes will be camelCased
        :param gen: optional TextBuffer
        :return: source code string
        """
        if gen is None:
            gen = TextBuffer()
            gen.writeln("from rick.form import RequestRecord, field", newlines=2)

        gen.writeln("class {}Record(RequestRecord):".format(snake_to_pascal(spec.table)))
        gen.writeln("fields = {", level=1)
        for field in spec.fields:
            gen.writeln(self._gen_field_src(field, camelcase, db_camelcase), level=2)
        gen.writeln("}", level=1)
        gen.writeln(gen.newline())
        return gen.read()
