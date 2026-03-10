import time
import threading
import logging
from dataclasses import dataclass, field

from rick.resource.console import ConsoleWriter

from pokie.constants import DI_TTY

logger = logging.getLogger(__name__)

# Maximum backoff in seconds
MAX_BACKOFF = 300


@dataclass
class JobState:
    job: object
    name: str
    interval: int = 0  # seconds between runs (0 = every iteration)
    max_retries: int = 0  # 0 = unlimited
    timeout: int = 0  # 0 = no timeout
    last_run: float = 0.0  # monotonic timestamp
    consecutive_failures: int = 0
    total_failures: int = 0
    backoff_until: float = 0.0  # monotonic timestamp; skip until this time


class JobRunner:
    """
    Manages job execution with per-job intervals, retry/backoff, and timeouts.
    """

    def __init__(self, job_list: list, tty: ConsoleWriter = None, silent: bool = False):
        self.states = []
        self.silent = silent
        self.tty = tty

        for job in job_list:
            state = JobState(
                job=job,
                name=type(job).__name__,
                interval=getattr(job, "job_interval", 0),
                max_retries=getattr(job, "job_max_retries", 0),
                timeout=getattr(job, "job_timeout", 0),
            )
            self.states.append(state)

    def _should_run(self, state: JobState, now: float) -> bool:
        # check interval
        if state.interval > 0 and now < state.last_run + state.interval:
            return False

        # check backoff
        if now < state.backoff_until:
            return False

        # check max retries
        if state.max_retries > 0 and state.consecutive_failures >= state.max_retries:
            return False

        return True

    def _run_with_timeout(self, state: JobState, di):
        """Run a job with a timeout using a thread."""
        result = {"error": None}

        def target():
            try:
                state.job.run(di)
            except Exception as e:
                result["error"] = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=state.timeout)

        if thread.is_alive():
            raise TimeoutError(
                "Job '{}' timed out after {}s".format(state.name, state.timeout)
            )

        if result["error"] is not None:
            raise result["error"]

    def _execute_job(self, state: JobState, di):
        """Execute a single job, handling timeout if configured."""
        now = time.monotonic()

        if not self._should_run(state, now):
            return

        try:
            if state.timeout > 0:
                self._run_with_timeout(state, di)
            else:
                state.job.run(di)

            # success: reset consecutive failures, update last_run
            state.consecutive_failures = 0
            state.last_run = time.monotonic()

        except Exception as e:
            state.consecutive_failures += 1
            state.total_failures += 1
            state.last_run = time.monotonic()

            # compute backoff: min(2^failures, MAX_BACKOFF)
            backoff = min(2 ** state.consecutive_failures, MAX_BACKOFF)
            state.backoff_until = time.monotonic() + backoff

            if not self.silent and self.tty:
                self.tty.error(
                    "Job '{}' failed (attempt {}): {}".format(
                        state.name, state.consecutive_failures, e
                    )
                )

    def run_once(self, di):
        """Run all jobs once."""
        for state in self.states:
            self._execute_job(state, di)

    def run_loop(self, di, signal_manager=None, abort_callback=None):
        """
        Run jobs continuously in a loop.

        :param di: dependency injection container
        :param signal_manager: optional signal manager for shutdown handling
        :param abort_callback: optional callback for SIGINT handling
        """
        import signal as signal_mod

        if signal_manager and abort_callback:
            signal_manager.add_handler(signal_mod.SIGINT, abort_callback)

        if not self.silent and self.tty:
            self.tty.write("\nRunning jobs, press CTRL+C to abort...")

        while True:
            for state in self.states:
                self._execute_job(state, di)
            # prevent busy-loop if no job provides its own sleep/idle
            time.sleep(0.1)
