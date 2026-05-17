from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import pytest

from ecg_rr_tool.analysis import OUTPUT_FIELDS, analyze_csv
from ecg_rr_tool.detectors.factory import create_detector
from ecg_rr_tool.export import write_output_csv
from ecg_rr_tool.io import InputDataError, read_bidmc_csv


FIXTURE = Path("tests/fixtures/bidmc_01_Signals_4000.csv")


def test_detector_factory_creates_wfdb_xqrs() -> None:
    detector = create_detector("wfdb_xqrs")

    assert detector.name == "wfdb_xqrs"
    assert detector.version is not None


def test_wfdb_adapter_detects_fixture_r_peaks_with_reasonable_rr() -> None:
    signals = read_bidmc_csv(FIXTURE)
    detector = create_detector("wfdb_xqrs")

    events = detector.detect(
        signals.ecg,
        sampling_rate_hz=signals.sampling_rate_hz,
        start_time_s=float(signals.time_s[0]),
    )

    assert 45 <= len(events) <= 55
    rr_values = [event.rr_ms for event in events if event.rr_ms is not None]
    assert rr_values
    assert all(300.0 <= rr <= 2000.0 for rr in rr_values)
    assert {event.detector_name for event in events} == {"wfdb_xqrs"}


def test_analysis_exports_io_contract_csv(tmp_path: Path) -> None:
    result = analyze_csv(FIXTURE)
    output_path = write_output_csv(result, tmp_path / "m3_result.csv")

    assert result.input_sample_count == 4000
    assert result.output_sample_count == 1600
    assert 45 <= result.r_peak_count <= 55
    assert result.rr_out_of_range_count == 0

    with output_path.open(newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert reader.fieldnames == list(OUTPUT_FIELDS)
    assert len(rows) == 1600
    r_peak_rows = [row for row in rows if row["r_peak_sample_index"]]
    assert len(r_peak_rows) == result.r_peak_count
    assert all(row["r_peak_time_s"] for row in r_peak_rows)
    assert all(row["detector_name"] == "wfdb_xqrs" for row in r_peak_rows)
    assert all(row["quality_flag"] == "ok" for row in r_peak_rows)
    assert any(row["rr_ms"] for row in r_peak_rows)


def test_cli_smoke_generates_output_csv(tmp_path: Path) -> None:
    output_path = tmp_path / "cli_result.csv"

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "ecg_rr_tool.cli",
            str(FIXTURE),
            str(output_path),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert output_path.exists()
    assert "input_rows: 4000" in completed.stdout
    assert "output_rows: 1600" in completed.stdout
    assert "detector_name: wfdb_xqrs" in completed.stdout
    assert "r_peak_count:" in completed.stdout


def test_missing_required_field_reports_clear_error(tmp_path: Path) -> None:
    bad_csv = tmp_path / "missing_ppg.csv"
    bad_csv.write_text("Time [s], II\n0,0.1\n0.008,0.2\n", encoding="utf-8")

    with pytest.raises(InputDataError, match="Missing required columns"):
        read_bidmc_csv(bad_csv)
