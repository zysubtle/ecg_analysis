# M6 Acceptance Report

## 1. Scope Summary

本项目当前为桌面端 ECG RR 研究 / 工程分析工具。当前能力包括：

1. 读取 BIDMC CSV；
2. 对字段名执行 `strip()` 后匹配 `Time [s]`、`II`、`PLETH`；
3. 校验原始采样率约为 125 Hz；
4. 在 125 Hz 原始 ECG 上使用 `wfdb_xqrs` 检测 R 峰；
5. 将 ECG、PPG、时间戳同步输出为 50 Hz；
6. 将 R 峰映射到 50 Hz 输出行；
7. 导出符合 IO Contract 的 CSV；
8. 提供 CLI；
9. 提供 Tkinter + Canvas 最小 GUI；
10. 提供 GUI headless self-test。

本项目不作为医疗诊断软件，不输出医疗诊断结论。

## 2. Technical Stack

| 项目 | 当前状态 |
|---|---|
| Python | 3.11+ |
| Runtime dependencies | `numpy==2.4.5`, `scipy==1.17.1`, `wfdb==4.3.1` |
| Detector | `wfdb_xqrs` |
| Detector adapter | `ecg_rr_tool/detectors/wfdb_detector.py` |
| CLI entry | `python -m ecg_rr_tool.cli` |
| GUI entry | `python -m ecg_rr_tool.gui` |
| GUI stack | Tkinter + Canvas |
| Fixture | `tests/fixtures/bidmc_01_Signals_4000.csv` |

## 3. Input / Output Contract Summary

输入 CSV：

- `Time [s]`：时间戳，单位秒；
- ` II` / `II`：ECG 单导联；
- ` PLETH` / `PLETH`：PPG；
- 读取时字段名按 `strip()` 后匹配；
- 原始采样率固定按约 125 Hz 校验。

输出 CSV 字段顺序：

```text
time_s_50hz
ecg_50hz
ppg_50hz
r_peak_sample_index
r_peak_time_s
rr_ms
detector_name
quality_flag
```

主输出 CSV 按 50 Hz 采样点逐行输出。非 R 峰行的 R 峰 / RR / detector / quality 字段为空。

## 4. CLI Acceptance

CLI 验收命令：

```bash
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m6_cli_smoke.csv
```

预期：

- `--version` 可运行；
- `--about` 明确研究 / 工程工具边界；
- fixture smoke test 可生成符合 IO Contract 的 CSV；
- `outputs/*.csv` 不进入 PR。

## 5. GUI Acceptance

GUI 验收命令：

```bash
python -m ecg_rr_tool.gui --help
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
```

预期：

- GUI 模块 import 不创建窗口；
- `--help` 可运行；
- `--self-test` 不依赖真实显示环境；
- self-test 调用现有 analysis 流程并构造 waveform / marker 坐标；
- GUI 不直接调用 WFDB API。

## 6. Fixture Smoke Test Results

基于 `tests/fixtures/bidmc_01_Signals_4000.csv` 的 smoke test 结果：

| 指标 | 结果 |
|---|---:|
| 输入行数 | 4000 |
| 输出行数 | 1600 |
| 估计采样率 | 125.000000 Hz |
| detector | `wfdb_xqrs` |
| detector version | 4.3.1 |
| R 峰数量 | 50 |
| RR min | 624 ms |
| RR median | 640 ms |
| RR max | 656 ms |
| RR out_of_range | 0 |
| waveform points | 1600 |
| marker 数量 | 50 |

该 fixture 只作为 smoke test / 回归测试样例，不代表总体准确性。

## 7. Executed Test Commands

默认环境命令：

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
python -m ecg_rr_tool.gui --help
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m6_cli_smoke.csv
```

功能性验收环境命令：

```bash
env PYTHONPATH=/private/tmp/ecg_m3_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pytest
env PYTHONPATH=/private/tmp/ecg_m3_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m ecg_rr_tool.cli --version
env PYTHONPATH=/private/tmp/ecg_m3_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m ecg_rr_tool.cli --about
env PYTHONPATH=/private/tmp/ecg_m3_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m ecg_rr_tool.gui --help
env PYTHONPATH=/private/tmp/ecg_m3_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
env PYTHONPATH=/private/tmp/ecg_m3_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m6_cli_smoke.csv
git check-ignore --no-index outputs/m6_cli_smoke.csv
git diff --check
git status --short
```

## 8. Acceptance Conclusion

结论：M1-M5 功能范围在正式依赖环境中通过 M6 smoke 验收。

本轮实际结果：

- 默认 Python 3.13.12 环境缺少 `numpy`，因此 `pytest`、GUI self-test 和 CLI smoke 在默认环境中因缺少 runtime 依赖失败；
- 正式依赖环境 `/private/tmp/ecg_m3_deps` 使用 Python 3.12.13，`pytest` 结果为 `27 passed`；
- GUI self-test 通过；
- CLI fixture smoke test 通过；
- `outputs/m6_cli_smoke.csv` 已删除且未提交。

已确认：

- CLI 可用；
- GUI self-test 可用；
- 输出字段与 IO Contract 一致；
- detector 仍通过 adapter 封装；
- GUI / CLI / 导出模块未直接调用 WFDB API；
- `outputs/*.csv` 运行产物不进入 PR；
- 文档明确研究 / 工程工具边界。

## 9. Known Limitations

- 仅使用单个 fixture 做 smoke test；
- 无参考标注，不能计算准确率、召回率或 F1；
- 第三方 detector 结果不等于临床有效性证明；
- GUI 是最小可视化，不支持缩放、滚动、复杂交互或人工编辑 R 峰；
- 当前不做 HRV、PPG IBI、批量处理、多导联融合或桌面安装包；
- 当前没有系统性覆盖噪声、早搏、漏搏、信号中断等异常场景。

## 10. Boundary Statement

本项目仅用于研究 / 工程分析。本项目不是医疗诊断软件，不应被用于医疗诊断、治疗决策或临床准确性声明。
