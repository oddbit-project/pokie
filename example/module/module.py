from example.module.constants import SVC_SAMPLE
from pokie.core import BaseModule


class Module(BaseModule):
    name = "module"
    description = "Example module"

    services = {
        SVC_SAMPLE: 'module.service.SampleService',
    }

    cmd = {}

    def build(self):
        pass
