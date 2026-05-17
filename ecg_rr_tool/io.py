"""Input handling for BIDMC-style CSV files."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np


EXPECTED_SAMPLING_RATE_HZ = 125.0
SAMPLING_RATE_TOLERANCE_HZ = 0.5
REQUIRED_COLUMNS = ("Time [s]", "II", "PLETH")


class InputDataError(ValueError):
    """Raised when an input CSV does not match the expected contract."""


@dataclass(frozen=True)
class BidmcSignals:
    path: Path
    time_s: np.ndarray
    ecg: np.ndarray
    ppg: np.ndarray
    sampling_rate_hz: float

    @property
    def sample_count(self) -> int:
        return int(self.time_s.size)


def read_bidmc_csv(path: str | Path) -> BidmcSignals:
    csv_path = Path(path)
    if not csv_path.exists():
        raise InputDataError(f"Input CSV does not exist: {csv_path}")
    if not csv_path.is_file():
        raise InputDataError(f"Input path is not a file: {csv_path}")

    with csv_path.open(newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise InputDataError(f"CSV has no header: {csv_path}")
        columns = _normalized_columns(reader.fieldnames)
        _require_columns(columns)

        time_values: list[float] = []
        ecg_values: list[float] = []
        ppg_values: list[float] = []
        for line_number, row in enumerate(reader, start=2):
            try:
                time_values.append(float(row[columns["Time [s]"]]))
                ecg_values.append(float(row[columns["II"]]))
                ppg_values.append(float(row[columns["PLETH"]]))
            except (TypeError, ValueError) as exc:
                raise InputDataError(f"Invalid numeric value at CSV line {line_number}: {exc}") from exc

    if len(time_values) < 2:
        raise InputDataError("Input CSV must contain at least two samples")

    time_s = np.asarray(time_values, dtype=float)
    ecg = np.asarray(ecg_values, dtype=float)
    ppg = np.asarray(ppg_values, dtype=float)
    _validate_monotonic_time(time_s)
    sampling_rate_hz = estimate_sampling_rate_hz(time_s)
    _validate_sampling_rate(sampling_rate_hz)

    return BidmcSignals(
        path=csv_path,
        time_s=time_s,
        ecg=ecg,
        ppg=ppg,
        sampling_rate_hz=sampling_rate_hz,
    )


def estimate_sampling_rate_hz(time_s: np.ndarray) -> float:
    duration_s = float(time_s[-1] - time_s[0])
    if duration_s <= 0:
        raise InputDataError("Timestamps must span a positive duration")
    return float((time_s.size - 1) / duration_s)


def _normalized_columns(fieldnames: list[str]) -> dict[str, str]:
    columns: dict[str, str] = {}
    duplicates: list[str] = []
    for raw_name in fieldnames:
        normalized = raw_name.strip()
        if normalized in columns:
            duplicates.append(normalized)
        columns[normalized] = raw_name

    if duplicates:
        duplicate_list = ", ".join(sorted(set(duplicates)))
        raise InputDataError(f"Duplicate CSV columns after strip(): {duplicate_list}")
    return columns


def _require_columns(columns: dict[str, str]) -> None:
    missing = [name for name in REQUIRED_COLUMNS if name not in columns]
    if missing:
        raise InputDataError(f"Missing required columns after strip(): {', '.join(missing)}")


def _validate_monotonic_time(time_s: np.ndarray) -> None:
    if not bool(np.all(np.diff(time_s) > 0)):
        raise InputDataError("Timestamps must be strictly increasing")


def _validate_sampling_rate(sampling_rate_hz: float) -> None:
    delta = abs(sampling_rate_hz - EXPECTED_SAMPLING_RATE_HZ)
    if delta > SAMPLING_RATE_TOLERANCE_HZ:
        raise InputDataError(
            "Estimated sampling rate must be approximately "
            f"{EXPECTED_SAMPLING_RATE_HZ:g} Hz; got {sampling_rate_hz:.6f} Hz"
        )
