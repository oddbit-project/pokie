import os

import pytest
import sys
from pokie.core import CliCommand


class PyTestCmd(CliCommand):
    description = "run pytest"
    skipargs = True

    def run(self, args) -> bool:
        args = []
        if len(sys.argv) > 2:
            args = sys.argv[2:]
        self.tty.write(
            self.tty.colorizer.white("[Pokie]", attr="bold")
            + " Running pytest with: {}".format(str(args))
        )
        sys.exit(pytest.main(args, plugins=["pytest_pokie"]))
