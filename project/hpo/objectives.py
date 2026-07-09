"""
Compatibility stub.

See project/hpo/search_space.py for the full explanation. `evaluate_config`
and `RobustSchedule` are imported unconditionally by `project/algorithms/
ifpoax.py` (and `evaluate_config` by fpa.py / pso.py), but every experiment
in this repository monkey-patches both names with the real benchmark
objective (F1-F13 / CEC2017 / shifted variants) and a lightweight mock
schedule via `benchmark_tester.AlgorithmRunner` before `run()` is called.
Neither function below is ever executed by any script in this repository.
"""


def evaluate_config(theta, rung_def, seeds, site, mode, t, trial_id, log_prefix="",
                     model_type=None, feature_scheme=None):
    raise NotImplementedError(
        "stub: evaluate_config is always monkey-patched by "
        "benchmark_tester.AlgorithmRunner during the experiments in this repo."
    )


class RobustSchedule:
    """Placeholder — always monkey-patched (return_value=MockRobustSchedule(...))
    by benchmark_tester.AlgorithmRunner before use."""

    def __init__(self, total_steps=None, *args, **kwargs):
        raise NotImplementedError(
            "stub: RobustSchedule is always monkey-patched by "
            "benchmark_tester.AlgorithmRunner during the experiments in this repo."
        )
