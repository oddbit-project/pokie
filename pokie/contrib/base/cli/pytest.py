import os

import pytest
import sys
from pokie.core import CliCommand


class PyTestCmd(CliCommand):
    description = "run pytest"
    skipargs = True

    def run(self, args) -> bool:
        args = sys.argv[2:] if len(sys.argv) > 2 else []
        self.tty.write(
            self.tty.colorizer.white("[Pokie]", attr="bold")
            + f" Running pytest with: {str(args)}"
        )
        sys.exit(pytest.main(args, plugins=["pytest_pokie"]))
