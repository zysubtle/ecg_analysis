# M4 Codex Task｜CLI 与导出体验完善

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

M4：CLI 与导出体验完善。

---

## 2. 已确认 Owner 决策

以下 S0 决策不得擅自改变：

1. 正式主 detector 为 `wfdb_xqrs`。
2. 不保留自研 fallback。
3. R 峰检测在 125 Hz 原始 ECG 上完成，再映射到 50 Hz 输出行。
4. 输入 fixture 固定为 `tests/fixtures/bidmc_01_Signals_4000.csv`。
5. 输出 CSV 字段必须遵守 `docs/04_IO_CONTRACT.md`。
6. 项目仅为研究 / 工程分析工具，不是医疗诊断软件。
7. 当前不做 HR、HRV、PPG IBI、批量处理、完整 GUI、桌面端打包或临床准确性声明。

---

## 3. 本轮目标

在不改变核心算法、detector 策略和 IO Contract 的前提下，完善 CLI 与导出体验，使 M3 已实现的分析流程更适合后续 GUI 调用和工程验收。

本轮完成后，应做到：

1. CLI 使用方式清晰、错误提示清晰；
2. 输入 / 输出路径处理更稳健；
3. 输出 CSV 仍严格符合 IO Contract；
4. runtime 产物不会进入 PR；
5. 基于 fixture 的 CLI smoke test 与错误场景测试更完整；
6. Runbook 中有清晰的 CLI 使用说明。

---

## 4. 本轮非目标

本轮不做：

1. 不改变 `wfdb_xqrs` detector 方案；
2. 不修改 R 峰检测算法参数，除非只是为了修复明确 bug；
3. 不改变输出 CSV 字段；
4. 不新增 `hr_bpm`、HRV 或医疗诊断字段；
5. 不实现完整 GUI；
6. 不做批量处理；
7. 不做桌面端打包；
8. 不新增参考标注准确性评估；
9. 不提交 `outputs/` 下的运行产物。

---

## 5. 允许修改范围

允许新增或修改：

- `ecg_rr_tool/cli.py`
- `ecg_rr_tool/export.py`
- `ecg_rr_tool/io.py`，仅限错误提示或边界处理，不改变输入契约
- `ecg_rr_tool/analysis.py`，仅限 summary / 返回信息组织，不改变算法策略
- `tests/` 下与 M4 CLI / export / error handling 相关的测试
- `docs/09_CODEX_RUNBOOK.md`
- `docs/10_CODEX_NEXT_TASK.md`
- `README.md`，如需要补充最小 CLI 示例
- `.gitignore`，如需要确认 `outputs/` 产物不入仓库

---

## 6. 不允许修改范围

未经 Owner 决策，不得修改：

1. `docs/04_IO_CONTRACT.md` 中已确认的输出字段；
2. 输入字段：`Time [s]`、` II` / `II`、` PLETH` / `PLETH`；
3. 原始采样率 125 Hz；
4. 目标输出采样率 50 Hz；
5. 主 detector：`wfdb_xqrs`；
6. fallback 策略：不保留自研 fallback；
7. Python 版本策略：Python 3.11+；
8. 依赖版本，除非修复明确安装冲突且必须报告；
9. GUI 范围；
10. 项目用途边界。

如果发现必须改变以上任何内容，必须暂停并在 Codex 输出中列为 S0 Owner 决策项。

---

## 7. CLI 体验要求

必须保留 M3 的基本命令形式：

```bash
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m4_bidmc_01_result.csv
```

必须保留：

```bash
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
```

建议增强：

1. `--help` 文案包含：用途边界、输入 CSV、输出 CSV、默认 detector、示例命令；
2. 成功运行后继续输出稳定的 key-value summary，至少包括：
   - `input_rows`
   - `output_rows`
   - `estimated_sampling_rate_hz`
   - `detector_name`
   - `detector_version`
   - `r_peak_count`
   - `rr_ms` 摘要
   - `output_csv`
3. 对以下错误给出清晰 stderr，不输出 traceback：
   - 输入文件不存在；
   - 缺失必要字段；
   - 字段 strip 后重复；
   - 时间戳非严格递增；
   - 采样率不是约 125 Hz；
   - detector 名称未知；
   - 输出路径不可写或输出目录无法创建；
4. 成功退出码为 `0`；工程 / 数据处理错误建议退出码为 `2`；argparse 用法错误可以保持默认行为；
5. 不输出医疗诊断结论。

可选增强，但不得破坏原有命令：

- 增加 `--quiet`：只输出必要结果；
- 增加 `--overwrite`：如果你决定保护已有输出文件不被覆盖，则必须提供该选项，并更新测试与 runbook；
- 增加 `--detector wfdb_xqrs` 的明确测试。

如果上述可选增强会导致复杂度变大，可以不做。

---

## 8. 导出体验要求

1. 输出 CSV 字段顺序必须与 `ecg_rr_tool.analysis.OUTPUT_FIELDS` 保持一致；
2. 输出 CSV 必须按 50 Hz 采样点逐行输出；
3. 非 R 峰行的 R 峰 / RR / detector / quality 字段为空；
4. R 峰行必须填充：
   - `r_peak_sample_index`
   - `r_peak_time_s`
   - `rr_ms`，第一个 R 峰可以为空
   - `detector_name`
   - `quality_flag`
5. 不新增 HR、HRV、医疗诊断字段；
6. 输出目录可自动创建；
7. 运行生成的 `outputs/*.csv` 不得提交入 PR。

---

## 9. 测试要求

至少新增或更新以下测试：

1. CLI `--help` 能正常运行，并包含核心关键词；
2. CLI `--version` 能正常运行；
3. CLI `--about` 能正常运行，并包含非医疗诊断边界说明；
4. CLI fixture smoke：
   - 输入 `tests/fixtures/bidmc_01_Signals_4000.csv`；
   - 输出到临时目录或 `outputs/m4_bidmc_01_result.csv`；
   - 检查退出码为 0；
   - 检查输出 CSV 存在；
   - 检查输出行数为 1600；
   - 检查 R 峰数量在合理范围，建议 `45 <= n_peaks <= 55`；
   - 检查 RR 均在 `300-2000 ms`；
5. 缺失字段错误测试；
6. 字段 strip 后重复错误测试；
7. 时间戳非单调错误测试；
8. 采样率异常错误测试；
9. 未知 detector 错误测试；
10. 输出目录自动创建测试；
11. 确认 `outputs/*.csv` 不进入 git diff。

如果现有测试已覆盖部分内容，可以复用并补充，不要重复堆测试。

---

## 10. 文档要求

更新 `docs/09_CODEX_RUNBOOK.md`，至少包含：

1. 依赖安装说明；
2. CLI 版本检查命令；
3. CLI 分析 fixture 的命令；
4. 输出 CSV 字段简述；
5. 常见错误及含义；
6. 明确说明 `outputs/` 是运行产物目录，不应提交结果 CSV；
7. 明确说明本项目不是医疗诊断软件。

如 README 已有 CLI 示例，可同步简短更新；不要写成长篇文档。

---

## 11. 建议测试命令

请至少执行并报告以下命令：

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
python -m ecg_rr_tool.cli --help
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m4_bidmc_01_result.csv
git status --short
git diff --check
```

如果默认 Python 环境缺少依赖，请说明实际使用的 Python 解释器、依赖安装位置和完整测试命令。功能性验收以安装正式依赖后的环境为准。

运行 smoke test 后，如果生成了 `outputs/m4_bidmc_01_result.csv`，不要把它提交入 PR。

---

## 12. 通过标准

M4 通过需要满足：

1. CLI 保留 M3 基本命令形式；
2. `--version`、`--about`、`--help` 可用；
3. fixture CLI smoke test 通过；
4. 输出 CSV 字段、字段顺序和行组织符合 IO Contract；
5. 错误场景有清晰 stderr，不输出 traceback；
6. 测试覆盖主要 CLI / export / error handling 场景；
7. Runbook 已更新；
8. 未改变 detector 策略、算法策略、IO Contract、依赖策略；
9. PR 不包含 `outputs/*.csv` 运行产物；
10. `git diff --check` 通过。

---

## 13. 失败时应报告的信息

如果无法完成，请报告：

1. 未满足的通过标准；
2. 失败的测试命令；
3. 关键错误日志；
4. 是否是依赖环境、CLI、CSV 读取、导出、测试或文档问题；
5. 是否需要 Owner 新增 S0 决策；
6. 建议如何拆分下一轮任务。

---

## 14. Codex 输出摘要要求

完成后请输出：

1. Summary；
2. Changed files；
3. 是否改变算法 / detector / IO Contract / 依赖版本；
4. CLI 行为变化说明；
5. Test commands；
6. Test results；
7. Fixture smoke test summary，包括：
   - 输入行数；
   - 输出行数；
   - 估计采样率；
   - R 峰数量；
   - RR 范围；
   - 输出 CSV 路径；
8. Known limitations；
9. Owner decision needed，如无请写“无”；
10. 未完成事项。

---

## 15. M4 完成记录

状态：已完成。

完成内容：

1. 已完善 CLI `--help`、`--version`、`--about` 和 fixture 分析命令体验；
2. 已补充输入文件不存在、缺字段、字段 strip 后重复、时间戳异常、采样率异常、未知 detector 等错误场景的清晰 stderr；
3. 已确认输出 CSV 字段和顺序仍由 `ecg_rr_tool.analysis.OUTPUT_FIELDS` 控制；
4. 已确认输出目录可自动创建；
5. 已确认 `outputs/*.csv` 运行产物不进入 PR；
6. 已更新 Runbook 和 README 的最小 CLI 使用说明；
7. 已新增 M4 CLI / export / error handling 测试。

下一步占位：M5 可进入最小 GUI 与波形可视化。
