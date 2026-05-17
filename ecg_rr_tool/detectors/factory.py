"""Detector factory."""

from __future__ import annotations

from ecg_rr_tool.detectors.base import RPeakDetector


def create_detector(name: str = "wfdb_xqrs") -> RPeakDetector:
    """Create a detector adapter by name."""
    normalized = name.strip().lower().replace("-", "_")
    if normalized in {"wfdb_xqrs", "wfdb", "xqrs"}:
        from ecg_rr_tool.detectors.wfdb_detector import WFDBXQRSDetector

        return WFDBXQRSDetector()

    raise ValueError(f"Unknown detector: {name}")
