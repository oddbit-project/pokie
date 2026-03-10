from pokie.util.cli_args import ArgParser


class TestArgParser:
    def test_init_defaults(self):
        parser = ArgParser()
        assert parser.failed is False
        assert parser.error_message == ""

    def test_error_sets_failed(self):
        parser = ArgParser()
        parser.error("something went wrong")
        assert parser.failed is True
        assert parser.error_message == "something went wrong"

    def test_format_parameters_no_args(self):
        parser = ArgParser(add_help=False)
        result = parser.format_parameters()
        assert isinstance(result, str)

    def test_format_parameters_with_args(self):
        parser = ArgParser(add_help=False)
        parser.add_argument("name", type=str, help="the name")
        parser.add_argument("-v", "--verbose", action="store_true", help="verbose output")
        result = parser.format_parameters()
        assert "name" in result
        assert "verbose" in result

    def test_parse_invalid_args_sets_failed(self):
        parser = ArgParser(add_help=False)
        parser.add_argument("required_arg", type=str)
        parser.parse_args([])
        assert parser.failed is True
        assert len(parser.error_message) > 0

    def test_parse_valid_args(self):
        parser = ArgParser(add_help=False)
        parser.add_argument("name", type=str)
        args = parser.parse_args(["hello"])
        assert parser.failed is False
        assert args.name == "hello"
