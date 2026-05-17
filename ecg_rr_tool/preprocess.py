"""Signal preprocessing for the ECG RR pipeline."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.signal import resample_poly

from ecg_rr_tool.io import BidmcSignals


TARGET_SAMPLING_RATE_HZ = 50.0


@dataclass(frozen=True)
class DownsampledSignals:
    time_s: np.ndarray
    ecg: np.ndarray
    ppg: np.ndarray
    sampling_rate_hz: float = TARGET_SAMPLING_RATE_HZ

    @property
    def sample_count(self) -> int:
        return int(self.time_s.size)


def downsample_to_50hz(signals: BidmcSignals) -> DownsampledSignals:
    """Synchronously downsample ECG and PPG from 125 Hz to 50 Hz."""
    ecg_50hz = resample_poly(signals.ecg, up=2, down=5)
    ppg_50hz = resample_poly(signals.ppg, up=2, down=5)
    output_count = min(int(ecg_50hz.size), int(ppg_50hz.size))

    ecg_50hz = np.asarray(ecg_50hz[:output_count], dtype=float)
    ppg_50hz = np.asarray(ppg_50hz[:output_count], dtype=float)
    time_50hz = float(signals.time_s[0]) + np.arange(output_count, dtype=float) / TARGET_SAMPLING_RATE_HZ

    return DownsampledSignals(
        time_s=time_50hz,
        ecg=ecg_50hz,
        ppg=ppg_50hz,
    )
