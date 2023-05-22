import os
from argparse import ArgumentParser
from pathlib import Path
from pokie.codegen.template import TemplateProcessor
from pokie.core import CliCommand


class TplGenCommand(CliCommand):
    def arguments(self, parser: ArgumentParser):
        parser.add_argument("name", type=str, help="new module name")
        parser.add_argument("path", type=str, help="where to create the module")

    def get_template_path(self, args) -> Path:
        raise RuntimeError("abstract method")

    def get_vars(self, args):
        return {}

    def run(self, args) -> bool:
        dest_path = Path(args.path) / Path(args.name)
        if dest_path.exists():
            self.tty.error(
                "error: directory '{}' already exists".format(str(dest_path))
            )
            return False

        tpl_path = self.get_template_path(args)
        vars = self.get_vars(args)

        self.tty.write(self.tty.colorizer.white("generating structure..."))
        processor = TemplateProcessor([tpl_path])
        processor.process(tpl_path, dest_path, vars, self.tty)
        self.tty.write(self.tty.colorizer.green("template processed sucessfully!"))
        return True


class ModuleGenCmd(TplGenCommand):
    description = "create module structure"

    def get_template_path(self, args) -> Path:
        return (
            Path(os.path.dirname(__file__))
            / Path("..")
            / Path("template")
            / Path("module")
        )

    def get_vars(self, args):
        return {"{module_name}": args.name, "{ModuleName}": args.name.capitalize()}
