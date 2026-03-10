# Jobs

Jobs are background tasks that run continuously in a cooperative loop. They are useful for operations such as
sending emails, processing queues, or performing periodic maintenance. Jobs are defined in modules and executed
via the `job:run` CLI command.

## Defining a Job

A job class must implement the `Injectable` and `Runnable` mixins from Rick:

```python
from rick.base import Di
from rick.mixin import Injectable, Runnable


class MyJob(Injectable, Runnable):
    def __init__(self, di: Di):
        super().__init__(di)

    def run(self, di: Di):
        # perform work here
        pass
```

Register jobs in a module by adding them to the `jobs` list:

```python
class Module(BaseModule):
    name = "my_module"

    jobs = [
        "my_module.job.MyJob",
    ]
```

## Job Runner

The job runner executes all registered jobs in a loop. It supports per-job configuration for intervals,
retries, and timeouts via optional class attributes.

### Job Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `job_interval` | `int` | `0` | Seconds between runs. `0` means run every iteration. |
| `job_max_retries` | `int` | `0` | Max consecutive failures before the job is skipped. `0` means unlimited. |
| `job_timeout` | `int` | `0` | Seconds before a run is terminated. `0` means no timeout. |

### Per-Job Intervals

Set `job_interval` to control how often a job runs. The job runner tracks the last run time and skips
execution until the interval has elapsed:

```python
class HourlyJob(Injectable, Runnable):
    job_interval = 3600  # run once per hour

    def run(self, di: Di):
        # this runs at most once per hour
        pass
```

This replaces the need for `IdleJob`-style sleep patterns. Jobs with `job_interval = 0` (the default) run on
every iteration of the loop.

### Retry and Backoff

When a job raises an exception, the runner tracks consecutive failures and applies exponential backoff:

- **Backoff formula:** `min(2^consecutive_failures, 300)` seconds
- After a successful run, the consecutive failure counter resets to zero
- If `job_max_retries` is set, the job is skipped entirely once the limit is reached

```python
class FragileJob(Injectable, Runnable):
    job_max_retries = 5  # stop after 5 consecutive failures

    def run(self, di: Di):
        # if this fails 5 times in a row, it stops running
        pass
```

### Timeouts

Set `job_timeout` to limit how long a single run can take. If the timeout is exceeded, the run is
terminated and counted as a failure:

```python
class TimedJob(Injectable, Runnable):
    job_timeout = 30  # abort if run takes longer than 30 seconds

    def run(self, di: Di):
        # long-running work that should not exceed 30 seconds
        pass
```

### Combining Attributes

All attributes can be combined:

```python
class RobustJob(Injectable, Runnable):
    job_interval = 60      # run every 60 seconds
    job_max_retries = 3    # stop after 3 consecutive failures
    job_timeout = 10       # abort runs longer than 10 seconds

    def run(self, di: Di):
        pass
```

## IdleJob

The built-in `IdleJob` provides a configurable sleep between job loop iterations. It defaults to 15 seconds
and can be configured via the `job_idle_interval` config key:

```python
from pokie.contrib.base.job import IdleJob
```

For new applications, using `job_interval` on individual jobs is preferred over relying on `IdleJob` for
pacing, as it provides more granular control.

## Running Jobs

### Continuous Mode

```shell
$ python main.py job:run
```

Runs all jobs in an infinite loop. Press `Ctrl+C` for graceful shutdown.

### Listing Jobs

```shell
$ python main.py job:list
```

Displays all registered jobs grouped by module.
