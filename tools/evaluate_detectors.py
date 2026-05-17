"""Temporary M2a detector evaluation script.

This script is intentionally outside the product CLI and adapter layer. It is
for comparing candidate libraries on the repository fixture only.
"""

from __future__ import annotations

import argparse
import csv
import importlib
import importlib.metadata
import json
import math
import os
import statistics
import sys
import tempfile
import traceback
import warnings
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence


REQUIRED_COLUMNS = ("Time [s]", "II", "PLETH")
RR_REASONABLE_MIN_MS = 300.0
RR_REASONABLE_MAX_MS = 2000.0

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "ecg_m2a_matplotlib"))
os.environ.setdefault("MPLBACKEND", "Agg")
warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated as an API.*",
    category=UserWarning,
)


class OptionalDependencyError(RuntimeError):
    """Raised when an evaluation-only optional dependency cannot be imported."""


@dataclass(frozen=True)
class FixtureData:
    path: str
    sample_count: int
    sampling_rate_hz: float
    time_s: list[float]
    ecg: list[float]
    ppg: list[float]


@dataclass(frozen=True)
class DetectorResult:
    detector_name: str
    status: str
    detector_version: str | None
    r_peak_count: int | None
    first_r_peak_times_s: list[float]
    rr_count: int
    rr_min_ms: float | None
    rr_median_ms: float | None
    rr_max_ms: float | None
    rr_out_of_range_count: int
    rr_all_in_reasonable_range: bool | None
    maps_to_io_contract: bool
    quality_flag: str
    error_message: str | None = None


def read_bidmc_csv(path: Path) -> FixtureData:
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")
        normalized = {name.strip(): name for name in reader.fieldnames}
        missing = [name for name in REQUIRED_COLUMNS if name not in normalized]
        if missing:
            raise ValueError(f"Missing required columns after strip(): {missing}")

        time_s: list[float] = []
        ecg: list[float] = []
        ppg: list[float] = []
        for row in reader:
            time_s.append(float(row[normalized["Time [s]"]]))
            ecg.append(float(row[normalized["II"]]))
            ppg.append(float(row[normalized["PLETH"]]))

    fs = estimate_sampling_rate_hz(time_s)
    return FixtureData(
        path=str(path),
        sample_count=len(time_s),
        sampling_rate_hz=fs,
        time_s=time_s,
        ecg=ecg,
        ppg=ppg,
    )


def estimate_sampling_rate_hz(time_s: Sequence[float]) -> float:
    if len(time_s) < 2:
        raise ValueError("At least two timestamps are required")
    duration_s = time_s[-1] - time_s[0]
    if duration_s <= 0:
        raise ValueError("Timestamps must be increasing")
    return (len(time_s) - 1) / duration_s


def version_for(distribution_name: str) -> str | None:
    try:
        return importlib.metadata.version(distribution_name)
    except importlib.metadata.PackageNotFoundError:
        return None


def _import_or_error(module_name: str, distribution_name: str | None = None):
    try:
        module = importlib.import_module(module_name)
    except Exception as exc:  # pragma: no cover - environment dependent
        raise OptionalDependencyError(f"import failed for {module_name}: {exc}") from exc
    return module


def _normalize_peak_indices(peaks: Iterable[object], sample_count: int) -> list[int]:
    normalized: list[int] = []
    for peak in peaks:
        if peak is None:
            continue
        idx = int(round(float(peak)))
        if 0 <= idx < sample_count:
            normalized.append(idx)
    return sorted(set(normalized))


def _peak_times_from_indices(indices: Sequence[int], time_s: Sequence[float], fs: float) -> list[float]:
    if not indices:
        return []
    start = time_s[0]
    return [time_s[idx] if idx < len(time_s) else start + idx / fs for idx in indices]


def _summarize(
    detector_name: str,
    detector_version: str | None,
    peak_indices: Sequence[int],
    data: FixtureData,
) -> DetectorResult:
    peak_indices = _normalize_peak_indices(peak_indices, data.sample_count)
    peak_times = _peak_times_from_indices(peak_indices, data.time_s, data.sampling_rate_hz)
    rr_ms = [
        (peak_times[i] - peak_times[i - 1]) * 1000.0
        for i in range(1, len(peak_times))
        if math.isfinite(peak_times[i]) and math.isfinite(peak_times[i - 1])
    ]
    out_of_range = [
        rr
        for rr in rr_ms
        if rr < RR_REASONABLE_MIN_MS or rr > RR_REASONABLE_MAX_MS
    ]
    rr_all_reasonable = bool(rr_ms) and not out_of_range
    quality_flag = "ok" if peak_indices and rr_all_reasonable else "unknown"
    return DetectorResult(
        detector_name=detector_name,
        status="ok",
        detector_version=detector_version,
        r_peak_count=len(peak_indices),
        first_r_peak_times_s=[round(value, 3) for value in peak_times[:8]],
        rr_count=len(rr_ms),
        rr_min_ms=round(min(rr_ms), 3) if rr_ms else None,
        rr_median_ms=round(statistics.median(rr_ms), 3) if rr_ms else None,
        rr_max_ms=round(max(rr_ms), 3) if rr_ms else None,
        rr_out_of_range_count=len(out_of_range),
        rr_all_in_reasonable_range=rr_all_reasonable,
        maps_to_io_contract=bool(peak_indices),
        quality_flag=quality_flag,
    )


def _failure(
    detector_name: str,
    status: str,
    detector_version: str | None,
    error_message: str,
) -> DetectorResult:
    return DetectorResult(
        detector_name=detector_name,
        status=status,
        detector_version=detector_version,
        r_peak_count=None,
        first_r_peak_times_s=[],
        rr_count=0,
        rr_min_ms=None,
        rr_median_ms=None,
        rr_max_ms=None,
        rr_out_of_range_count=0,
        rr_all_in_reasonable_range=None,
        maps_to_io_contract=False,
        quality_flag="error",
        error_message=error_message,
    )


def evaluate_neurokit2(data: FixtureData) -> DetectorResult:
    name = "NeuroKit2"
    dist = "neurokit2"
    version = version_for(dist)
    try:
        nk = _import_or_error("neurokit2", dist)
        _, info = nk.ecg_peaks(data.ecg, sampling_rate=data.sampling_rate_hz, method="neurokit")
        peaks = info.get("ECG_R_Peaks", [])
        return _summarize(name, version, peaks, data)
    except OptionalDependencyError as exc:
        return _failure(name, "import_failed", version, str(exc))
    except Exception as exc:  # pragma: no cover - candidate-library behavior
        return _failure(name, "runtime_failed", version, _format_error(exc))


def evaluate_wfdb_xqrs(data: FixtureData) -> DetectorResult:
    name = "WFDB XQRS"
    dist = "wfdb"
    version = version_for(dist)
    try:
        np = _import_or_error("numpy")
        processing = _import_or_error("wfdb.processing", dist)
        peaks = processing.xqrs_detect(
            sig=np.asarray(data.ecg, dtype=float),
            fs=float(data.sampling_rate_hz),
            verbose=False,
        )
        return _summarize(name, version, peaks, data)
    except OptionalDependencyError as exc:
        return _failure(name, "import_failed", version, str(exc))
    except Exception as exc:  # pragma: no cover - candidate-library behavior
        return _failure(name, "runtime_failed", version, _format_error(exc))


def evaluate_biosppy(data: FixtureData) -> DetectorResult:
    name = "BioSPPy"
    dist = "biosppy"
    version = version_for(dist)
    try:
        np = _import_or_error("numpy")
        biosppy_ecg = _import_or_error("biosppy.signals.ecg", dist)
        out = biosppy_ecg.ecg(
            signal=np.asarray(data.ecg, dtype=float),
            sampling_rate=float(data.sampling_rate_hz),
            show=False,
        )
        try:
            peaks = out["rpeaks"]
        except (TypeError, KeyError):
            peaks = out[2]
        return _summarize(name, version, peaks, data)
    except OptionalDependencyError as exc:
        return _failure(name, "import_failed", version, str(exc))
    except Exception as exc:  # pragma: no cover - candidate-library behavior
        return _failure(name, "runtime_failed", version, _format_error(exc))


def evaluate_sleepecg(data: FixtureData) -> DetectorResult:
    name = "SleepECG"
    dist = "sleepecg"
    version = version_for(dist)
    try:
        np = _import_or_error("numpy")
        sleepecg = _import_or_error("sleepecg", dist)
        ecg = np.asarray(data.ecg, dtype=float)
        try:
            peaks = sleepecg.detect_heartbeats(ecg, fs=float(data.sampling_rate_hz))
        except TypeError:
            peaks = sleepecg.detect_heartbeats(ecg, float(data.sampling_rate_hz))
        return _summarize(name, version, peaks, data)
    except OptionalDependencyError as exc:
        return _failure(name, "import_failed", version, str(exc))
    except Exception as exc:  # pragma: no cover - candidate-library behavior
        return _failure(name, "runtime_failed", version, _format_error(exc))


def evaluate_heartpy(data: FixtureData) -> DetectorResult:
    name = "HeartPy"
    dist = "heartpy"
    version = version_for(dist)
    try:
        np = _import_or_error("numpy")
        hp = _import_or_error("heartpy", dist)
        working_data, _ = hp.process(
            np.asarray(data.ecg, dtype=float),
            sample_rate=float(data.sampling_rate_hz),
            clean_rr=False,
            report_time=False,
        )
        peaklist = working_data.get("peaklist", [])
        removed = set(working_data.get("removed_beats", []))
        peaks = [peak for peak in peaklist if peak not in removed]
        return _summarize(name, version, peaks, data)
    except OptionalDependencyError as exc:
        return _failure(name, "import_failed", version, str(exc))
    except Exception as exc:  # pragma: no cover - candidate-library behavior
        return _failure(name, "runtime_failed", version, _format_error(exc))


def evaluate_scipy_find_peaks(data: FixtureData) -> DetectorResult:
    name = "SciPy find_peaks baseline"
    version = version_for("scipy")
    try:
        np = _import_or_error("numpy")
        signal = _import_or_error("scipy.signal", "scipy")
        ecg = np.asarray(data.ecg, dtype=float)
        fs = float(data.sampling_rate_hz)
        centered = ecg - np.nanmedian(ecg)
        sos = signal.butter(2, [5.0, 20.0], btype="bandpass", fs=fs, output="sos")
        filtered = signal.sosfiltfilt(sos, centered)
        min_distance = max(1, int(round(0.3 * fs)))
        prominence = max(float(np.nanstd(filtered)) * 0.5, 1e-9)
        positive_peaks, positive_props = signal.find_peaks(
            filtered,
            distance=min_distance,
            prominence=prominence,
        )
        negative_peaks, negative_props = signal.find_peaks(
            -filtered,
            distance=min_distance,
            prominence=prominence,
        )
        positive_score = _median_prominence(positive_props.get("prominences", []))
        negative_score = _median_prominence(negative_props.get("prominences", []))
        peaks = negative_peaks if negative_score > positive_score else positive_peaks
        return _summarize(name, version, peaks, data)
    except OptionalDependencyError as exc:
        return _failure(name, "import_failed", version, str(exc))
    except Exception as exc:  # pragma: no cover - candidate-library behavior
        return _failure(name, "runtime_failed", version, _format_error(exc))


def _median_prominence(values: Sequence[float]) -> float:
    if len(values) == 0:
        return 0.0
    return float(statistics.median(float(value) for value in values))


def _format_error(exc: Exception) -> str:
    message = "".join(traceback.format_exception_only(type(exc), exc)).strip()
    return message.replace("\n", " | ")


EVALUATORS: tuple[Callable[[FixtureData], DetectorResult], ...] = (
    evaluate_neurokit2,
    evaluate_wfdb_xqrs,
    evaluate_biosppy,
    evaluate_sleepecg,
    evaluate_heartpy,
    evaluate_scipy_find_peaks,
)


def evaluate_all(data: FixtureData) -> list[DetectorResult]:
    return [evaluator(data) for evaluator in EVALUATORS]


def _print_text(data: FixtureData, results: Sequence[DetectorResult]) -> None:
    print(f"fixture: {data.path}")
    print(f"samples: {data.sample_count}")
    print(f"estimated_sampling_rate_hz: {data.sampling_rate_hz:.6f}")
    print()
    for result in results:
        print(f"[{result.detector_name}]")
        print(f"  status: {result.status}")
        print(f"  version: {result.detector_version or 'unknown'}")
        if result.error_message:
            print(f"  error: {result.error_message}")
        else:
            print(f"  r_peak_count: {result.r_peak_count}")
            print(f"  first_r_peak_times_s: {result.first_r_peak_times_s}")
            print(
                "  rr_ms: "
                f"count={result.rr_count}, "
                f"min={result.rr_min_ms}, "
                f"median={result.rr_median_ms}, "
                f"max={result.rr_max_ms}, "
                f"out_of_range={result.rr_out_of_range_count}"
            )
            print(f"  maps_to_io_contract: {result.maps_to_io_contract}")
            print(f"  quality_flag: {result.quality_flag}")
        print()


def _json_payload(data: FixtureData, results: Sequence[DetectorResult]) -> dict[str, object]:
    return {
        "fixture": {
            "path": data.path,
            "sample_count": data.sample_count,
            "estimated_sampling_rate_hz": data.sampling_rate_hz,
        },
        "results": [asdict(result) for result in results],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate M2a detector candidates on the fixture CSV.")
    parser.add_argument("csv_path", type=Path, help="Repository-relative BIDMC fixture CSV path.")
    parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    data = read_bidmc_csv(args.csv_path)
    results = evaluate_all(data)
    if args.format == "json":
        print(json.dumps(_json_payload(data, results), indent=2, sort_keys=True))
    else:
        _print_text(data, results)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
