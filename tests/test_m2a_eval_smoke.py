from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


FIXTURE = Path("tests/fixtures/bidmc_01_Signals_4000.csv")
SCRIPT = Path("tools/evaluate_detectors.py")


def _load_eval_module():
    spec = importlib.util.spec_from_file_location("m2a_evaluate_detectors", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_m2a_script_reads_fixture_with_stripped_columns() -> None:
    module = _load_eval_module()
    data = module.read_bidmc_csv(FIXTURE)

    assert data.sample_count == 4000
    assert abs(data.sampling_rate_hz - 125.0) < 1e-6
    assert len(data.time_s) == len(data.ecg) == len(data.ppg) == 4000


def test_m2a_script_reports_all_candidate_results_without_hard_failure() -> None:
    module = _load_eval_module()
    data = module.read_bidmc_csv(FIXTURE)
    results = module.evaluate_all(data)

    detector_names = {result.detector_name for result in results}
    assert detector_names == {
        "NeuroKit2",
        "WFDB XQRS",
        "BioSPPy",
        "SleepECG",
        "HeartPy",
        "SciPy find_peaks baseline",
    }
    assert {result.status for result in results} <= {"ok", "import_failed", "runtime_failed"}
