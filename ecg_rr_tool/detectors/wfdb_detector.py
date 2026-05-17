"""WFDB XQRS detector adapter."""

from __future__ import annotations

from importlib import metadata
from typing import Sequence

import numpy as np
from wfdb import processing

from ecg_rr_tool.detectors.base import RPeakEvent


class WFDBXQRSDetector:
    """Adapter around `wfdb.processing.xqrs_detect`."""

    name = "wfdb_xqrs"

    def __init__(self) -> None:
        try:
            self.version = metadata.version("wfdb")
        except metadata.PackageNotFoundError:
            self.version = None

    def detect(
        self,
        ecg: Sequence[float],
        sampling_rate_hz: float,
        start_time_s: float = 0.0,
    ) -> list[RPeakEvent]:
        if sampling_rate_hz <= 0:
            raise ValueError("sampling_rate_hz must be positive")

        signal = np.asarray(ecg, dtype=float)
        if signal.ndim != 1:
            raise ValueError("ecg must be a one-dimensional sequence")
        if signal.size < 2:
            raise ValueError("ecg must contain at least two samples")

        peak_indices = processing.xqrs_detect(
            sig=signal,
            fs=float(sampling_rate_hz),
            verbose=False,
        )
        normalized_indices = sorted(
            {
                int(index)
                for index in peak_indices
                if 0 <= int(index) < signal.size
            }
        )

        events: list[RPeakEvent] = []
        previous_time_s: float | None = None
        for index in normalized_indices:
            peak_time_s = float(start_time_s) + (index / float(sampling_rate_hz))
            rr_ms = None if previous_time_s is None else (peak_time_s - previous_time_s) * 1000.0
            events.append(
                RPeakEvent(
                    r_peak_sample_index=index,
                    r_peak_time_s=peak_time_s,
                    rr_ms=rr_ms,
                    detector_name=self.name,
                    detector_version=self.version,
                    quality_flag="ok",
                )
            )
            previous_time_s = peak_time_s

        return events
