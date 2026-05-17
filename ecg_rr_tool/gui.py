"""Minimal Tkinter GUI for ECG RR analysis."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence


CANVAS_WIDTH = 900
CANVAS_HEIGHT = 360
CANVAS_PADDING = 24


def build_waveform_points(
    output_rows: Sequence[dict[str, Any]],
    width: int = CANVAS_WIDTH,
    height: int = CANVAS_HEIGHT,
    padding: int = CANVAS_PADDING,
) -> list[tuple[float, float]]:
    """Map 50 Hz ECG output rows to Canvas coordinates."""
    ecg_values = [_safe_float(row.get("ecg_50hz")) for row in output_rows]
    ecg_values = [value for value in ecg_values if value is not None]
    if not ecg_values:
        return []

    x_values = _x_positions(len(ecg_values), width, padding)
    y_values = _scaled_y_positions(ecg_values, height, padding)
    return list(zip(x_values, y_values, strict=True))


def build_r_peak_marker_positions(
    output_rows: Sequence[dict[str, Any]],
    width: int = CANVAS_WIDTH,
    height: int = CANVAS_HEIGHT,
    padding: int = CANVAS_PADDING,
) -> list[tuple[float, float]]:
    """Map R-peak rows to Canvas marker coordinates."""
    waveform_points = build_waveform_points(output_rows, width=width, height=height, padding=padding)
    if not waveform_points:
        return []

    markers: list[tuple[float, float]] = []
    for row_index, row in enumerate(output_rows):
        if row.get("r_peak_sample_index") in ("", None):
            continue
        try:
            marker_index = int(row["r_peak_sample_index"])
        except (TypeError, ValueError):
            marker_index = row_index
        if 0 <= marker_index < len(waveform_points):
            markers.append(waveform_points[marker_index])
    return markers


def run_self_test(input_csv: str | Path) -> dict[str, Any]:
    """Run GUI-independent analysis and coordinate mapping checks."""
    from ecg_rr_tool.analysis import analyze_csv

    result = analyze_csv(input_csv)
    waveform_points = build_waveform_points(result.output_rows)
    marker_positions = build_r_peak_marker_positions(result.output_rows)
    if not waveform_points:
        raise RuntimeError("GUI self-test produced no waveform points")
    if not 45 <= len(marker_positions) <= 55:
        raise RuntimeError(f"GUI self-test marker count is outside smoke range: {len(marker_positions)}")

    return {
        "input_rows": result.input_sample_count,
        "output_rows": result.output_sample_count,
        "r_peak_count": result.r_peak_count,
        "waveform_points": len(waveform_points),
        "markers": len(marker_positions),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ecg-rr-gui",
        description=(
            "Minimal Tkinter ECG RR engineering GUI. "
            "This tool is not medical diagnostic software."
        ),
    )
    parser.add_argument(
        "--self-test",
        metavar="CSV",
        help="Run GUI coordinate smoke test without creating a Tk window.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.self_test:
        try:
            summary = run_self_test(args.self_test)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print(f"input_rows: {summary['input_rows']}")
        print(f"output_rows: {summary['output_rows']}")
        print(f"r_peak_count: {summary['r_peak_count']}")
        print(f"waveform_points: {summary['waveform_points']}")
        print(f"markers: {summary['markers']}")
        return 0

    try:
        return _run_tk_app()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _run_tk_app() -> int:
    import tkinter as tk

    root = tk.Tk()
    app = ECGToolApp(root)
    app.pack()
    root.mainloop()
    return 0


class ECGToolApp:
    """Small Tkinter UI that delegates analysis to the existing pipeline."""

    def __init__(self, root: Any) -> None:
        import tkinter as tk

        self.root = root
        self.tk = tk
        self.frame = tk.Frame(root, padx=12, pady=12)
        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.status = tk.StringVar(value="Ready")

        root.title("ECG RR Engineering Tool")
        self._build_widgets()

    def pack(self) -> None:
        self.frame.pack(fill="both", expand=True)

    def _build_widgets(self) -> None:
        tk = self.tk
        tk.Label(
            self.frame,
            text="ECG RR Engineering Tool - not medical diagnostic software",
            font=("TkDefaultFont", 13, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))

        tk.Button(self.frame, text="Choose Input CSV", command=self._choose_input).grid(row=1, column=0, sticky="w")
        tk.Entry(self.frame, textvariable=self.input_path, width=88).grid(row=1, column=1, columnspan=2, sticky="ew")

        tk.Button(self.frame, text="Choose Output CSV", command=self._choose_output).grid(row=2, column=0, sticky="w")
        tk.Entry(self.frame, textvariable=self.output_path, width=88).grid(row=2, column=1, columnspan=2, sticky="ew")

        tk.Button(self.frame, text="Run Analysis", command=self._run_analysis).grid(row=3, column=0, sticky="w", pady=8)
        tk.Label(self.frame, textvariable=self.status).grid(row=3, column=1, columnspan=2, sticky="w")

        self.summary = tk.Text(self.frame, width=90, height=8)
        self.summary.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, 8))

        self.canvas = tk.Canvas(self.frame, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white", highlightthickness=1)
        self.canvas.grid(row=5, column=0, columnspan=3, sticky="nsew")

        self.frame.columnconfigure(1, weight=1)
        self.frame.rowconfigure(5, weight=1)
        self._draw_empty_canvas()

    def _choose_input(self) -> None:
        from tkinter import filedialog

        selected = filedialog.askopenfilename(
            title="Choose BIDMC CSV",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not selected:
            return
        self.input_path.set(selected)
        if not self.output_path.get():
            self.output_path.set(str(Path("outputs") / f"{Path(selected).stem}_gui_result.csv"))

    def _choose_output(self) -> None:
        from tkinter import filedialog

        initial = self.output_path.get() or "outputs/gui_result.csv"
        selected = filedialog.asksaveasfilename(
            title="Choose output CSV",
            initialfile=Path(initial).name,
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if selected:
            self.output_path.set(selected)

    def _run_analysis(self) -> None:
        from tkinter import messagebox

        input_csv = self.input_path.get().strip()
        output_csv = self.output_path.get().strip()
        if not input_csv:
            self._show_error("Input CSV is required")
            return
        if not output_csv:
            self._show_error("Output CSV is required")
            return

        self.status.set("Running analysis...")
        self.root.update_idletasks()
        try:
            from ecg_rr_tool.analysis import analyze_csv
            from ecg_rr_tool.export import write_output_csv

            result = analyze_csv(input_csv)
            output_path = write_output_csv(result, output_csv)
        except Exception as exc:
            self._show_error(str(exc))
            messagebox.showerror("Analysis failed", str(exc))
            return

        self._update_summary(result, output_path)
        self._draw_result(result.output_rows)
        self.status.set("Analysis complete")

    def _show_error(self, message: str) -> None:
        self.status.set(f"Error: {message}")

    def _update_summary(self, result: Any, output_path: Path) -> None:
        rr_summary = result.rr_summary
        lines = [
            f"input_rows: {result.input_sample_count}",
            f"output_rows: {result.output_sample_count}",
            f"estimated_sampling_rate_hz: {result.sampling_rate_hz:.6f}",
            f"detector_name: {result.detector_name}",
            f"detector_version: {result.detector_version or 'unknown'}",
            f"r_peak_count: {result.r_peak_count}",
            "rr_ms: "
            f"count={rr_summary['count']}, "
            f"min={_format_optional_float(rr_summary['min'])}, "
            f"median={_format_optional_float(rr_summary['median'])}, "
            f"max={_format_optional_float(rr_summary['max'])}, "
            f"out_of_range={rr_summary['out_of_range']}",
            f"output_csv: {output_path}",
        ]
        self.summary.delete("1.0", "end")
        self.summary.insert("1.0", "\n".join(lines))

    def _draw_empty_canvas(self) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(
            CANVAS_WIDTH / 2,
            CANVAS_HEIGHT / 2,
            text="50 Hz ECG waveform will appear here",
            fill="#555555",
        )

    def _draw_result(self, output_rows: Sequence[dict[str, Any]]) -> None:
        self.canvas.delete("all")
        self.canvas.create_text(12, 12, text="50 Hz ECG, R peaks marked", anchor="nw", fill="#333333")
        points = build_waveform_points(output_rows)
        markers = build_r_peak_marker_positions(output_rows)
        if len(points) > 1:
            flat_points = [coord for point in points for coord in point]
            self.canvas.create_line(*flat_points, fill="#1f5fbf", width=1)
        for x, y in markers:
            self.canvas.create_line(x, CANVAS_PADDING, x, CANVAS_HEIGHT - CANVAS_PADDING, fill="#d63b2f")
            self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="#d63b2f", outline="")


def _x_positions(count: int, width: int, padding: int) -> list[float]:
    if count <= 0:
        return []
    if count == 1:
        return [width / 2]
    usable_width = max(float(width - 2 * padding), 1.0)
    return [padding + (index / (count - 1)) * usable_width for index in range(count)]


def _scaled_y_positions(values: Sequence[float], height: int, padding: int) -> list[float]:
    if not values:
        return []
    value_min = min(values)
    value_max = max(values)
    usable_height = max(float(height - 2 * padding), 1.0)
    if value_max == value_min:
        return [height / 2 for _ in values]
    return [
        padding + (1.0 - ((value - value_min) / (value_max - value_min))) * usable_height
        for value in values
    ]


def _safe_float(value: Any) -> float | None:
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _format_optional_float(value: float | int | None) -> str:
    if value is None:
        return "none"
    return f"{float(value):.3f}"


if __name__ == "__main__":
    raise SystemExit(main())
