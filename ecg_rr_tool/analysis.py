"""Minimal ECG analysis flow."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ecg_rr_tool.detectors.base import RPeakEvent
from ecg_rr_tool.detectors.factory import create_detector
from ecg_rr_tool.io import BidmcSignals, read_bidmc_csv
from ecg_rr_tool.preprocess import TARGET_SAMPLING_RATE_HZ, DownsampledSignals, downsample_to_50hz


OUTPUT_FIELDS = (
    "time_s_50hz",
    "ecg_50hz",
    "ppg_50hz",
    "r_peak_sample_index",
    "r_peak_time_s",
    "rr_ms",
    "detector_name",
    "quality_flag",
)
RR_REASONABLE_MIN_MS = 300.0
RR_REASONABLE_MAX_MS = 2000.0


@dataclass(frozen=True)
class AnalysisResult:
    input_path: Path
    input_sample_count: int
    output_sample_count: int
    sampling_rate_hz: float
    detector_name: str
    detector_version: str | None
    r_peak_events: list[RPeakEvent]
    output_rows: list[dict[str, Any]]

    @property
    def r_peak_count(self) -> int:
        return len(self.r_peak_events)

    @property
    def rr_values_ms(self) -> list[float]:
        return [float(event.rr_ms) for event in self.r_peak_events if event.rr_ms is not None]

    @property
    def rr_out_of_range_count(self) -> int:
        return sum(
            1
            for rr_ms in self.rr_values_ms
            if rr_ms < RR_REASONABLE_MIN_MS or rr_ms > RR_REASONABLE_MAX_MS
        )

    @property
    def rr_summary(self) -> dict[str, float | int | None]:
        values = self.rr_values_ms
        if not values:
            return {"count": 0, "min": None, "median": None, "max": None, "out_of_range": 0}
        return {
            "count": len(values),
            "min": min(values),
            "median": statistics.median(values),
            "max": max(values),
            "out_of_range": self.rr_out_of_range_count,
        }


def analyze_csv(input_path: str | Path, detector_name: str = "wfdb_xqrs") -> AnalysisResult:
    signals = read_bidmc_csv(input_path)
    detector = create_detector(detector_name)
    events = detector.detect(
        signals.ecg,
        sampling_rate_hz=signals.sampling_rate_hz,
        start_time_s=float(signals.time_s[0]),
    )
    downsampled = downsample_to_50hz(signals)
    output_rows = build_output_rows(signals, downsampled, events)
    detector_version = events[0].detector_version if events else getattr(detector, "version", None)

    return AnalysisResult(
        input_path=Path(input_path),
        input_sample_count=signals.sample_count,
        output_sample_count=downsampled.sample_count,
        sampling_rate_hz=signals.sampling_rate_hz,
        detector_name=getattr(detector, "name", detector_name),
        detector_version=detector_version,
        r_peak_events=events,
        output_rows=output_rows,
    )


def build_output_rows(
    source: BidmcSignals,
    downsampled: DownsampledSignals,
    events: list[RPeakEvent],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index in range(downsampled.sample_count):
        rows.append(
            {
                "time_s_50hz": float(downsampled.time_s[index]),
                "ecg_50hz": float(downsampled.ecg[index]),
                "ppg_50hz": float(downsampled.ppg[index]),
                "r_peak_sample_index": "",
                "r_peak_time_s": "",
                "rr_ms": "",
                "detector_name": "",
                "quality_flag": "",
            }
        )

    time_start_s = float(source.time_s[0])
    for event in events:
        mapped_index = int(round((event.r_peak_time_s - time_start_s) * TARGET_SAMPLING_RATE_HZ))
        if mapped_index < 0 or mapped_index >= len(rows):
            continue
        rows[mapped_index]["r_peak_sample_index"] = mapped_index
        rows[mapped_index]["r_peak_time_s"] = float(event.r_peak_time_s)
        rows[mapped_index]["rr_ms"] = "" if event.rr_ms is None else float(event.rr_ms)
        rows[mapped_index]["detector_name"] = event.detector_name
        rows[mapped_index]["quality_flag"] = event.quality_flag or "unknown"

    return rows
