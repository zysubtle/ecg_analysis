"""CSV export for analysis results."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

from ecg_rr_tool.analysis import OUTPUT_FIELDS, AnalysisResult


def write_output_csv(result: AnalysisResult, output_path: str | Path) -> Path:
    path = Path(output_path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise OSError(f"Could not create output directory '{path.parent}': {exc}") from exc

    if path.exists() and path.is_dir():
        raise OSError(f"Output path is a directory: {path}")

    try:
        with path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(OUTPUT_FIELDS))
            writer.writeheader()
            for row in result.output_rows:
                writer.writerow({field: _format_value(row[field]) for field in OUTPUT_FIELDS})
    except OSError as exc:
        raise OSError(f"Could not write output CSV '{path}': {exc}") from exc
    return path


def _format_value(value: Any) -> str:
    if value == "" or value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)
