"""Command line entry point for the ECG RR tool."""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path

from ecg_rr_tool import __version__


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecg-rr",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Desktop ECG RR engineering analysis tool. "
            "This tool is not medical diagnostic software."
        ),
        epilog=textwrap.dedent(
            """\
            Input CSV columns are matched after strip(): Time [s], II, PLETH.
            Default detector: wfdb_xqrs.

            Example:
              python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m4_bidmc_01_result.csv
            """
        ),
    )
    parser.add_argument("--version", action="version", version=f"ecg-rr-tool {__version__}")
    parser.add_argument(
        "--about",
        action="store_true",
        help="Print project boundary notice and exit.",
    )
    parser.add_argument(
        "--detector",
        default="wfdb_xqrs",
        help="Detector adapter name. Default: wfdb_xqrs.",
    )
    parser.add_argument("input_csv", nargs="?", help="Input BIDMC CSV path.")
    parser.add_argument("output_csv", nargs="?", help="Output IO Contract CSV path.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.about:
        print("This is an engineering/research ECG analysis tool, not medical diagnostic software.")
        return 0

    if args.input_csv is None and args.output_csv is None:
        parser.print_help()
        return 0
    if args.input_csv is None or args.output_csv is None:
        parser.error("input_csv and output_csv must be provided together")

    try:
        from ecg_rr_tool.analysis import analyze_csv
        from ecg_rr_tool.export import write_output_csv

        result = analyze_csv(Path(args.input_csv), detector_name=args.detector)
        output_path = write_output_csv(result, Path(args.output_csv))
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    rr_summary = result.rr_summary

    print(f"input_rows: {result.input_sample_count}")
    print(f"output_rows: {result.output_sample_count}")
    print(f"estimated_sampling_rate_hz: {result.sampling_rate_hz:.6f}")
    print(f"detector_name: {result.detector_name}")
    print(f"detector_version: {result.detector_version or 'unknown'}")
    print(f"r_peak_count: {result.r_peak_count}")
    print(
        "rr_ms: "
        f"count={rr_summary['count']}, "
        f"min={_format_optional_float(rr_summary['min'])}, "
        f"median={_format_optional_float(rr_summary['median'])}, "
        f"max={_format_optional_float(rr_summary['max'])}, "
        f"out_of_range={rr_summary['out_of_range']}"
    )
    print(f"output_csv: {output_path}")
    return 0


def _format_optional_float(value: float | int | None) -> str:
    if value is None:
        return "none"
    return f"{float(value):.3f}"


if __name__ == "__main__":
    raise SystemExit(main())
