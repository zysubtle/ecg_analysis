# M5 Codex Task｜最小 GUI 与波形可视化

## 0. 执行前必须阅读

请先阅读以下文档：

- `AGENTS.md`
- `docs/00_PROJECT_BRIEF.md`
- `docs/01_DECISION_LOG.md`
- `docs/02_MILESTONE_PLAN.md`
- `docs/03_ALGORITHM_SCOPE.md`
- `docs/04_IO_CONTRACT.md`
- `docs/05_DETECTOR_STRATEGY.md`
- `docs/06_THIRD_PARTY_EVAL.md`
- `docs/09_CODEX_RUNBOOK.md`
- `docs/10_CODEX_NEXT_TASK.md`

当前任务以本文件内容为准。

---

## 1. 当前里程碑

M5：最小 GUI 与波形可视化。

---

## 2. 已确认 Owner 决策

以下为 Owner 已确认的 S0 决策，不得擅自改变：

1. M3 正式主 detector 继续使用 `wfdb_xqrs`。
2. 继续保持不保留自研 fallback。
3. 最终运行环境允许 Python 3.11+。
4. 当前仍只基于 `tests/fixtures/bidmc_01_Signals_4000.csv` 做 smoke test 与工程合理性检查。
5. M5 GUI 框架采用 **Tkinter + Canvas**。
6. M5 不新增 PySide6、matplotlib 或其他 GUI / 绘图库依赖。
7. 本项目仍然只是研究 / 工程分析工具，不是医疗诊断软件。

---

## 3. 本轮目标

在不改变现有算法、detector、IO Contract 和依赖版本的前提下，实现一个最小桌面 GUI，用于：

1. 选择输入 BIDMC CSV；
2. 选择或填写输出 CSV 路径；
3. 调用现有 `analyze_csv()` 与 `write_output_csv()` 流程；
4. 显示 50 Hz ECG 波形；
5. 在 ECG 波形上标记 R 峰；
6. 显示基础分析摘要；
7. 导出符合 IO Contract 的 CSV；
8. 提供可在无显示环境中运行的 GUI 自检 / smoke test。

---

## 4. 本轮非目标

本轮不做：

1. 不更换 `wfdb_xqrs` detector；
2. 不修改 R 峰检测算法；
3. 不修改 RR 计算逻辑；
4. 不修改 `docs/04_IO_CONTRACT.md` 中已确认的输出字段；
5. 不新增 HR / HRV；
6. 不计算 PPG IBI；
7. 不做多导联融合；
8. 不做人工编辑 R 峰；
9. 不做复杂交互，例如缩放、拖拽、框选、滚动浏览、峰值手动增删；
10. 不做完整桌面安装包；
11. 不做临床准确性声明；
12. 不输出医疗诊断结论。

---

## 5. 允许修改范围

允许新增或修改：

- `ecg_rr_tool/gui.py`
- `ecg_rr_tool/` 下与 GUI 调用现有流程所需的轻量 helper，但不得改变算法行为；
- `tests/` 下与 M5 GUI / headless smoke 相关的测试；
- `pyproject.toml`，仅允许新增 GUI 入口脚本，例如 `ecg-rr-gui = "ecg_rr_tool.gui:main"`，不得新增依赖；
- `README.md`，补充 GUI 使用说明；
- `docs/09_CODEX_RUNBOOK.md`，补充 GUI 运行说明，并顺手统一 Python 版本描述为 Python 3.11+；
- `docs/10_CODEX_NEXT_TASK.md`，任务完成后可追加 M5 完成记录。

---

## 6. 不允许修改范围

未经 Owner 决策，不得修改：

1. 主 detector：`wfdb_xqrs`；
2. fallback 策略：不保留自研 fallback；
3. 输入字段：`Time [s]`、` II` / `II`、` PLETH` / `PLETH`；
4. 原始采样率：125 Hz；
5. 目标输出采样率：50 Hz；
6. R 峰检测时机：在 125 Hz 原始 ECG 上检测，再映射到 50 Hz 输出；
7. 输出 CSV 字段；
8. `requirements.txt` 中正式 runtime 依赖版本；
9. `pyproject.toml` 中现有依赖版本；
10. 医疗用途边界；
11. 示例 CSV 路径；
12. `.gitignore` 对 `outputs/*.csv` 的忽略规则。

如果发现必须改变上述任何内容，必须暂停并在 Codex 输出中列为 S0 Owner 决策项。

---

## 7. GUI 功能要求

建议实现文件：

```text
ecg_rr_tool/gui.py
```

建议启动命令：

```bash
python -m ecg_rr_tool.gui
```

如修改 `pyproject.toml`，可增加入口：

```bash
ecg-rr-gui
```

GUI 最小功能：

1. 窗口标题应体现：ECG RR Engineering Tool / 工程分析工具；
2. 明确显示用途边界：不是医疗诊断软件；
3. 提供“选择输入 CSV”按钮；
4. 输入 CSV 路径可显示在界面中；
5. 提供“选择输出 CSV”或输出路径输入框；
6. 输出路径默认可建议为 `outputs/<input_stem>_gui_result.csv`；
7. 提供“运行分析 / Run Analysis”按钮；
8. 运行时调用现有：
   - `ecg_rr_tool.analysis.analyze_csv`
   - `ecg_rr_tool.export.write_output_csv`
9. 分析成功后显示 summary：
   - 输入行数；
   - 输出行数；
   - 估计采样率；
   - detector 名称；
   - detector version；
   - R 峰数量；
   - RR min / median / max / out_of_range；
   - 输出 CSV 路径；
10. 使用 Tkinter Canvas 显示 50 Hz ECG 波形；
11. 在 Canvas 上标记 R 峰，最小实现可以使用竖线或小圆点；
12. 如果分析失败，用 messagebox 或状态栏显示清晰错误，不显示 traceback；
13. GUI 不直接调用 WFDB API，只能调用现有 analysis/export 层；
14. GUI 不新增医疗诊断文案。

---

## 8. 可视化要求

M5 只要求最小可视化，不要求复杂交互。

绘图建议：

1. 使用 `result.output_rows` 中的：
   - `time_s_50hz`
   - `ecg_50hz`
   - `r_peak_sample_index`
2. 在 Canvas 内将 50 Hz ECG 序列缩放到可见区域；
3. 横轴可按样本索引线性映射；
4. 纵轴可按 ECG 最小值 / 最大值线性映射；
5. 若 ECG 为常数或范围异常，应避免除零；
6. R 峰标记应与映射后的 `r_peak_sample_index` 对齐；
7. 可显示简单文字说明，例如 `50 Hz ECG, R peaks marked`；
8. 不要求坐标轴刻度、缩放、拖拽或多通道显示；
9. 不要求显示 PPG 波形。

为便于测试，建议将坐标映射逻辑拆为纯函数，例如：

```text
build_waveform_points(...)
build_r_peak_marker_positions(...)
```

这些函数应可在无 GUI display 的环境下测试。

---

## 9. Headless self-test 要求

由于 Codex / CI 环境可能没有桌面显示，必须提供不依赖真实窗口显示的自检方式。

建议实现：

```bash
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
```

`--self-test` 应完成：

1. 读取 fixture；
2. 调用现有分析流程；
3. 构造绘图所需 waveform points；
4. 构造 R 峰 marker positions；
5. 验证 R 峰数量合理；
6. 验证坐标数组非空；
7. 不创建 Tk root，或至少不依赖显示环境；
8. 输出简要 summary；
9. 返回 0。

允许另设 `--help`，但不要求复杂 CLI 参数。

---

## 10. 测试要求

至少新增或更新以下测试：

1. `ecg_rr_tool.gui` 可 import，且 import 不创建窗口；
2. GUI self-test 命令可在无显示环境下运行；
3. waveform 坐标映射函数对 fixture 输出非空坐标；
4. R 峰 marker 坐标数量与 R 峰行数量一致或在合理范围内；
5. 空数据 / 常数 ECG 等边界输入不会导致除零；
6. GUI 不直接调用 WFDB API；
7. M4 CLI smoke 不回归；
8. `outputs/*.csv` 运行产物不进入 PR。

注意：不要写必须真实弹窗的自动化测试，除非可以在无显示环境中稳定运行。

---

## 11. 建议测试命令

请至少执行并报告以下命令。可根据环境补充，但不能省略核心 smoke test。

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
python -m ecg_rr_tool.gui --help
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m5_cli_smoke.csv
git status --short
git diff --check
```

如果默认 Python 环境缺少依赖，应说明实际使用的 Python 解释器、依赖安装位置和完整测试命令。

执行 CLI smoke 产生的 `outputs/m5_cli_smoke.csv` 必须在测试后删除，不能提交。

---

## 12. 通过标准

M5 通过需要满足：

1. GUI 入口存在；
2. GUI 使用 Tkinter + Canvas；
3. 未新增 PySide6、matplotlib 或其他 GUI / 绘图库依赖；
4. GUI 可选择输入 CSV 和输出 CSV；
5. GUI 可运行现有分析流程；
6. GUI 可显示 50 Hz ECG 波形；
7. GUI 可标记 R 峰；
8. GUI 可导出符合 IO Contract 的 CSV；
9. GUI 错误提示清晰，不输出 traceback；
10. GUI 不直接调用 WFDB API；
11. GUI import / self-test 可在无显示环境中测试；
12. CLI 旧功能不回归；
13. `outputs/*.csv` 未进入 PR；
14. 文档说明 GUI 用法和非医疗用途边界；
15. 测试命令真实执行并通过，或清楚说明失败原因。

---

## 13. 失败时应报告的信息

如果无法完成，请报告：

1. 未满足的通过标准；
2. 失败的测试命令；
3. 关键错误日志；
4. 是否是 Tkinter、显示环境、依赖安装、数据处理、Canvas 绘图或导出问题；
5. 是否需要 Owner 新增 S0 决策；
6. 建议如何拆分下一轮任务。

---

## 14. Codex 输出摘要要求

完成后请输出：

1. Summary；
2. Changed files；
3. 是否新增依赖，如无请写“无新增依赖”；
4. GUI 入口位置；
5. GUI 功能摘要；
6. Test commands；
7. Test results；
8. Fixture GUI/self-test summary，包括：
   - 输入行数；
   - 输出行数；
   - R 峰数量；
   - waveform points 数量；
   - marker 数量；
9. Known limitations；
10. Owner decision needed，如无请写“无”；
11. 未完成事项。

---

## 15. M5 完成记录

状态：已完成。

完成内容：

1. 已实现 `python -m ecg_rr_tool.gui` Tkinter + Canvas 最小 GUI；
2. GUI 支持选择输入 CSV、选择输出 CSV、运行现有分析流程、显示 50 Hz ECG 波形、标记 R 峰、显示基础摘要并导出 CSV；
3. 已实现 `python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv`，可在无显示环境下完成分析和坐标映射自检；
4. 已新增 waveform / marker 坐标映射纯函数及边界输入测试；
5. 已确认 GUI 不直接调用 WFDB API；
6. 已新增 M5 GUI / headless smoke 测试；
7. 已更新 Runbook 和 README 的 GUI 使用说明；
8. 已确认 `outputs/*.csv` 运行产物不进入 PR。

下一步占位：M6 可进入验收、文档收敛与风险复盘。
