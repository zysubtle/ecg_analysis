from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import ecg_rr_tool.gui as gui
from ecg_rr_tool.analysis import analyze_csv


FIXTURE = Path("tests/fixtures/bidmc_01_Signals_4000.csv")


def test_gui_module_import_does_not_create_window() -> None:
    assert callable(gui.main)
    assert callable(gui.build_waveform_points)
    assert callable(gui.build_r_peak_marker_positions)


def test_gui_self_test_runs_headless() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "ecg_rr_tool.gui", "--self-test", str(FIXTURE)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, completed.stderr
    assert "input_rows: 4000" in completed.stdout
    assert "output_rows: 1600" in completed.stdout
    assert "r_peak_count: 50" in completed.stdout
    assert "waveform_points: 1600" in completed.stdout
    assert "markers: 50" in completed.stdout


def test_waveform_and_marker_mapping_for_fixture_output() -> None:
    result = analyze_csv(FIXTURE)

    points = gui.build_waveform_points(result.output_rows, width=500, height=200, padding=10)
    markers = gui.build_r_peak_marker_positions(result.output_rows, width=500, height=200, padding=10)
    peak_rows = [row for row in result.output_rows if row["r_peak_sample_index"] != ""]

    assert len(points) == result.output_sample_count
    assert len(markers) == len(peak_rows)
    assert 45 <= len(markers) <= 55
    assert all(10 <= x <= 490 for x, _ in points)
    assert all(10 <= y <= 190 for _, y in points)


def test_waveform_mapping_handles_empty_and_constant_ecg() -> None:
    assert gui.build_waveform_points([]) == []
    assert gui.build_r_peak_marker_positions([]) == []

    rows = [
        {"ecg_50hz": 1.0, "r_peak_sample_index": ""},
        {"ecg_50hz": 1.0, "r_peak_sample_index": 1},
        {"ecg_50hz": 1.0, "r_peak_sample_index": ""},
    ]
    points = gui.build_waveform_points(rows, width=300, height=100, padding=10)
    markers = gui.build_r_peak_marker_positions(rows, width=300, height=100, padding=10)

    assert len(points) == 3
    assert {y for _, y in points} == {50}
    assert len(markers) == 1


def test_gui_does_not_directly_call_wfdb_api() -> None:
    source = Path("ecg_rr_tool/gui.py").read_text(encoding="utf-8")

    assert "wfdb" not in source
    assert "xqrs_detect" not in source


def test_outputs_csv_is_ignored_for_m5_smoke() -> None:
    completed = subprocess.run(
        ["git", "check-ignore", "--no-index", "outputs/m5_cli_smoke.csv"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
