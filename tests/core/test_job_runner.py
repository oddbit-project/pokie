import time

from rick.base import Di
from rick.mixin import Injectable, Runnable
from rick.resource.console import ConsoleWriter

from pokie.core.job_runner import JobRunner, JobState


class CounterJob(Injectable, Runnable):
    def __init__(self, di: Di):
        super().__init__(di)
        self.counter = 0

    def run(self, di: Di):
        self.counter += 1


class FailingJob(Injectable, Runnable):
    def __init__(self, di: Di):
        super().__init__(di)
        self.counter = 0

    def run(self, di: Di):
        self.counter += 1
        raise RuntimeError("job failed")


class IntervalJob(Injectable, Runnable):
    job_interval = 1  # 1 second interval

    def __init__(self, di: Di):
        super().__init__(di)
        self.counter = 0

    def run(self, di: Di):
        self.counter += 1


class RetryJob(Injectable, Runnable):
    job_max_retries = 3

    def __init__(self, di: Di):
        super().__init__(di)
        self.counter = 0

    def run(self, di: Di):
        self.counter += 1
        raise RuntimeError("always fails")


class SlowJob(Injectable, Runnable):
    job_timeout = 1  # 1 second timeout

    def __init__(self, di: Di):
        super().__init__(di)
        self.counter = 0

    def run(self, di: Di):
        self.counter += 1
        time.sleep(10)  # much longer than timeout


class TestJobRunner:
    def _make_di(self):
        return Di()

    def test_run_once(self):
        di = self._make_di()
        job = CounterJob(di)
        runner = JobRunner([job], silent=True)
        runner.run_once(di)
        assert job.counter == 1

    def test_run_once_multiple_jobs(self):
        di = self._make_di()
        job1 = CounterJob(di)
        job2 = CounterJob(di)
        runner = JobRunner([job1, job2], silent=True)
        runner.run_once(di)
        assert job1.counter == 1
        assert job2.counter == 1

    def test_interval_skipping(self):
        di = self._make_di()
        job = IntervalJob(di)
        runner = JobRunner([job], silent=True)

        # first run should execute
        runner.run_once(di)
        assert job.counter == 1

        # immediate second run should be skipped (interval not elapsed)
        runner.run_once(di)
        assert job.counter == 1

    def test_interval_elapsed(self):
        di = self._make_di()
        job = IntervalJob(di)
        runner = JobRunner([job], silent=True)

        # first run
        runner.run_once(di)
        assert job.counter == 1

        # manually set last_run to the past so interval is elapsed
        runner.states[0].last_run = time.monotonic() - 2
        runner.run_once(di)
        assert job.counter == 2

    def test_retry_counting(self):
        di = self._make_di()
        job = RetryJob(di)
        runner = JobRunner([job], silent=True)
        state = runner.states[0]

        # run 3 times - all should attempt and fail
        for i in range(3):
            # reset backoff so we can run immediately
            state.backoff_until = 0
            runner.run_once(di)

        assert state.consecutive_failures == 3
        assert state.total_failures == 3
        assert job.counter == 3

        # 4th run should be skipped (max_retries=3 reached)
        state.backoff_until = 0
        runner.run_once(di)
        assert job.counter == 3  # not incremented

    def test_backoff_computation(self):
        di = self._make_di()
        job = FailingJob(di)
        runner = JobRunner([job], silent=True)
        state = runner.states[0]

        runner.run_once(di)
        assert state.consecutive_failures == 1
        # backoff should be min(2^1, 300) = 2 seconds
        assert state.backoff_until > time.monotonic()

    def test_success_resets_failures(self):
        di = self._make_di()
        job = CounterJob(di)
        runner = JobRunner([job], silent=True)
        state = runner.states[0]

        # artificially set failures
        state.consecutive_failures = 5
        state.total_failures = 10

        runner.run_once(di)
        assert state.consecutive_failures == 0
        assert state.total_failures == 10  # total is not reset

    def test_timeout(self):
        di = self._make_di()
        job = SlowJob(di)
        runner = JobRunner([job], silent=True)
        state = runner.states[0]

        start = time.monotonic()
        runner.run_once(di)
        elapsed = time.monotonic() - start

        # should have timed out after ~1 second, not 10
        assert elapsed < 5
        assert state.consecutive_failures == 1

    def test_no_interval_runs_every_time(self):
        di = self._make_di()
        job = CounterJob(di)
        runner = JobRunner([job], silent=True)

        runner.run_once(di)
        runner.run_once(di)
        runner.run_once(di)
        assert job.counter == 3

    def test_tty_error_output(self):
        import io
        di = self._make_di()
        job = FailingJob(di)
        tty = ConsoleWriter(stdout=io.StringIO(), stderr=io.StringIO())
        runner = JobRunner([job], tty=tty, silent=False)

        runner.run_once(di)

        output = tty.stderr.getvalue()
        assert "FailingJob" in output
        assert "failed" in output
