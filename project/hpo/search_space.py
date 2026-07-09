"""
Compatibility stub.

`project/algorithms/ifpoax.py`, `fpa.py`, and `pso.py` are copied byte-for-byte
from a larger private thesis project (rainfall-forecasting transformer HPO),
and unconditionally import `build_search_space`, `build_transformer_small_space`,
and `SearchSpace` from this module at module load time.

This repository is a standalone extraction containing only the origin-bias
benchmark audit (see project/algorithms/paper/). The real search-space
implementation belongs to the private thesis project and is not needed here:
every experiment in this repo runs through `benchmark_tester.AlgorithmRunner`
(project/algorithms/benchmark_tester.py), which monkey-patches all three of
these names with a mock search space and the real benchmark objective
(F1-F13 / CEC2017 / shifted variants) BEFORE the optimizer's `run()` method
is ever called. None of the functions below are executed by any script in
this repository; they exist solely so the unmodified algorithm files import
successfully.
"""


class SearchSpace:
    """Placeholder — never instantiated directly; benchmark_tester.py's
    MockSearchSpace is what is actually used at runtime."""
    pass


def build_search_space(model_type, preset=None):
    raise NotImplementedError(
        "stub: build_search_space is always monkey-patched by "
        "benchmark_tester.AlgorithmRunner during the experiments in this repo."
    )


def build_transformer_small_space(*args, **kwargs):
    raise NotImplementedError(
        "stub: build_transformer_small_space is always monkey-patched by "
        "benchmark_tester.AlgorithmRunner during the experiments in this repo."
    )
