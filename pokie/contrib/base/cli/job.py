import signal
from argparse import ArgumentParser
from typing import List

from rick.mixin import Injectable, Runnable
from rick.util.loader import load_class

from pokie.constants import DI_APP, DI_SIGNAL, DI_TTY
from pokie.contrib.base.cli.base import BaseCommand


def abort_jobs(di, signal_no, stack_trace):
    di.get(DI_TTY).write("\nCtrl+C pressed, exiting...")
    exit(0)


class JobBaseCmd(BaseCommand):
    def get_jobs(self) -> dict:
        result = {}
        for module_name, module in self.get_di().get(DI_APP).modules.items():
            jobs = getattr(module, "jobs", [])
            if len(jobs) > 0:
                result[module_name] = jobs
        return result


class JobListCmd(JobBaseCmd):
    description = "list registered job workers"

    def run(self, args) -> bool:
        for name, jobs in self.get_jobs().items():
            self.tty.write(f"Worker Jobs for module {name}:")
            for job in jobs:
                self.tty.write(self.tty.colorizer.white(f"   {job}", attr="bold"))

        return True


class JobRunCmd(JobBaseCmd):
    description = "run  all job workers"

    def run(self, args) -> bool:
        joblist = []
        di = self.get_di()

        # prepare job list
        for module_name, jobs in self.get_jobs().items():
            for job_name in jobs:
                self.tty.write(f"Preparing job  '{job_name}'...")
                job = load_class(job_name)
                if job is None:
                    raise ValueError(
                        f"Non-existing job class '{job_name}' in module {module_name}"
                    )
                if not issubclass(job, (Injectable, Runnable)):
                    raise RuntimeError(
                        "Class '{}' must implement Injectable, Runnable interfaces"
                    )
                joblist.append(job(di))

        # run job list
        joblist.reverse()
        self.tty.write("\nRunning jobs, press CTRL+C to abort...")

        # register clean shutdown
        di.get(DI_SIGNAL).add_handler(signal.SIGINT, abort_jobs)

        while True:
            for job in joblist:
                job.run(di)

        # unreachable
        return True
