"""
Compatibility stub.

Unlike project/hpo/search_space.py and project/hpo/objectives.py, the two
functions here ARE actually called at runtime: `ifpoax.py`'s `run()` method
imports this module locally (`from ..utils import mlflow_utils as MU`) rather
than through the module-level `mlflow` name that benchmark_tester.py patches,
so `heartbeat()` and `log_checkpoint()` execute for real during every run.

They are therefore implemented as safe no-ops rather than stubs that raise:
this repository does not need real MLflow heartbeat/checkpoint logging for
the benchmark audit, and no-opping them keeps the unmodified algorithm files
runnable without pulling in the private thesis project's MLflow setup.
"""


def heartbeat(interval, progress=None, step=None):
    """No-op: this repo does not need periodic run-alive signalling."""
    return None


def log_checkpoint(path, artifact_path=None):
    """No-op: this repo does not persist/upload optimizer checkpoints."""
    return None
