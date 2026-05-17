from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


FIXTURE = Path("tests/fixtures/bidmc_01_Signals_4000.csv")


def run_cli(*args: str | Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "ecg_rr_tool.cli", *[str(arg) for arg in args]],
        check=False,
        capture_output=True,
        text=True,
    )


def test_cli_help_contains_core_keywords() -> None:
    completed = run_cli("--help")

    assert completed.returncode == 0
    assert "not medical diagnostic software" in completed.stdout
    assert "Input CSV" in completed.stdout
    assert "Output IO Contract CSV" in completed.stdout
    assert "Default detector: wfdb_xqrs" in completed.stdout
    assert "tests/fixtures/bidmc_01_Signals_4000.csv" in completed.stdout


def test_cli_version_runs() -> None:
    completed = run_cli("--version")

    assert completed.returncode == 0
    assert completed.stdout.strip().startswith("ecg-rr-tool ")


def test_cli_about_contains_boundary_notice() -> None:
    completed = run_cli("--about")

    assert completed.returncode == 0
    assert "engineering/research ECG analysis tool" in completed.stdout
    assert "not medical diagnostic software" in completed.stdout


def test_cli_fixture_smoke_exports_contract_csv(tmp_path: Path) -> None:
    output_path = tmp_path / "nested" / "m4_result.csv"

    completed = run_cli(FIXTURE, output_path)

    assert completed.returncode == 0, completed.stderr
    assert output_path.exists()
    assert "input_rows: 4000" in completed.stdout
    assert "output_rows: 1600" in completed.stdout
    assert "estimated_sampling_rate_hz: 125.000000" in completed.stdout
    assert "detector_name: wfdb_xqrs" in completed.stdout
    assert "r_peak_count: 50" in completed.stdout

    with output_path.open(newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 1600
    peak_rows = [row for row in rows if row["r_peak_sample_index"]]
    assert 45 <= len(peak_rows) <= 55
    rr_values = [float(row["rr_ms"]) for row in peak_rows if row["rr_ms"]]
    assert rr_values
    assert all(300.0 <= rr <= 2000.0 for rr in rr_values)


def test_cli_missing_input_file_has_clear_error(tmp_path: Path) -> None:
    completed = run_cli(tmp_path / "missing.csv", tmp_path / "out.csv")

    assert completed.returncode == 2
    assert "Input CSV does not exist" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_missing_required_field_has_clear_error(tmp_path: Path) -> None:
    bad_csv = tmp_path / "missing_ppg.csv"
    bad_csv.write_text("Time [s],II\n0,0.1\n0.008,0.2\n", encoding="utf-8")

    completed = run_cli(bad_csv, tmp_path / "out.csv")

    assert completed.returncode == 2
    assert "Missing required columns after strip(): PLETH" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_duplicate_stripped_field_has_clear_error(tmp_path: Path) -> None:
    bad_csv = tmp_path / "duplicate.csv"
    bad_csv.write_text("Time [s], II,II,PLETH\n0,0.1,0.2,0.3\n0.008,0.2,0.3,0.4\n", encoding="utf-8")

    completed = run_cli(bad_csv, tmp_path / "out.csv")

    assert completed.returncode == 2
    assert "Duplicate CSV columns after strip(): II" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_non_monotonic_time_has_clear_error(tmp_path: Path) -> None:
    bad_csv = tmp_path / "non_monotonic.csv"
    bad_csv.write_text("Time [s],II,PLETH\n0,0.1,0.2\n0,0.2,0.3\n", encoding="utf-8")

    completed = run_cli(bad_csv, tmp_path / "out.csv")

    assert completed.returncode == 2
    assert "Timestamps must be strictly increasing" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_bad_sampling_rate_has_clear_error(tmp_path: Path) -> None:
    bad_csv = tmp_path / "bad_sampling_rate.csv"
    bad_csv.write_text("Time [s],II,PLETH\n0,0.1,0.2\n1,0.2,0.3\n2,0.3,0.4\n", encoding="utf-8")

    completed = run_cli(bad_csv, tmp_path / "out.csv")

    assert completed.returncode == 2
    assert "Estimated sampling rate must be approximately 125 Hz" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_unknown_detector_has_clear_error(tmp_path: Path) -> None:
    completed = run_cli("--detector", "unknown_detector", FIXTURE, tmp_path / "out.csv")

    assert completed.returncode == 2
    assert "Unknown detector: unknown_detector" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_outputs_csv_is_ignored_by_gitignore() -> None:
    completed = subprocess.run(
        ["git", "check-ignore", "--no-index", "outputs/m4_bidmc_01_result.csv"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0
