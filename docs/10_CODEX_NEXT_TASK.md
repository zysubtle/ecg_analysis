# M6 Codex Task｜验收、文档收敛与风险复盘

## 0. 执行前必须阅读

请先阅读以下文档：

- `AGENTS.md`
- `README.md`
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

M6：验收、文档收敛与风险复盘。

---

## 2. 已确认 Owner 决策

以下为 Owner 已确认的 S0 决策，不得擅自改变：

1. 本项目是研究 / 工程分析工具，不作为医疗诊断软件。
2. 输入数据为 BIDMC CSV。
3. 原始采样率固定为 125 Hz。
4. 时间戳字段为 `Time [s]`，单位秒。
5. ECG 字段为 ` II` / `II`，读取时需 `strip()` 后匹配。
6. PPG 字段为 ` PLETH` / `PLETH`，读取时需 `strip()` 后匹配。
7. ECG、PPG 和时间戳同步输出为 50 Hz。
8. R 峰检测优先在 125 Hz 原始 ECG 上完成，再映射到 50 Hz 输出行。
9. 正式主 detector 为 `wfdb_xqrs`。
10. 不保留自研 fallback。
11. 最终运行环境允许 Python 3.11+，不强制兼容 Python 3.10。
12. GUI 技术栈为 Tkinter + Canvas。
13. 示例 CSV 固定为 `tests/fixtures/bidmc_01_Signals_4000.csv`。
14. 单个 fixture 只作为 smoke test / 回归测试样例，不代表总体准确性或临床有效性。

---

## 3. 本轮目标

对 M1-M5 已完成内容做最终验收、文档收敛和风险复盘。

本轮完成后，应得到：

1. 一个清晰的 M6 验收报告；
2. 更新后的 README / Runbook / Milestone Plan；
3. 统一的 Python 3.11+ 环境说明；
4. 统一的 CLI / GUI 示例；
5. 明确的风险与限制说明；
6. 完整的 smoke test 结果记录；
7. 不包含运行产物的干净 PR。

---

## 4. 本轮非目标

本轮不做：

1. 不修改算法逻辑；
2. 不修改 WFDB XQRS detector adapter；
3. 不更换 detector；
4. 不新增 fallback；
5. 不修改 IO Contract 字段；
6. 不新增 HR / HRV；
7. 不新增 PPG IBI；
8. 不扩展 GUI 功能；
9. 不做人工编辑 R 峰；
10. 不做临床准确性声明；
11. 不做桌面端安装包；
12. 不新增第三方依赖。

---

## 5. 允许修改范围

允许新增或修改：

- `README.md`
- `docs/01_DECISION_LOG.md`
- `docs/02_MILESTONE_PLAN.md`
- `docs/03_ALGORITHM_SCOPE.md`
- `docs/04_IO_CONTRACT.md`，仅限文字澄清，不得改变字段
- `docs/05_DETECTOR_STRATEGY.md`，仅限状态同步和风险说明
- `docs/07_ACCEPTANCE_REPORT.md`，如果不存在则新增
- `docs/08_RISK_REVIEW.md`，如果不存在则新增
- `docs/09_CODEX_RUNBOOK.md`
- `docs/10_CODEX_NEXT_TASK.md`

如确有必要，可新增极小的文档一致性测试，但不建议修改源码。

---

## 6. 不允许修改范围

未经 Owner 决策，不得修改：

1. `ecg_rr_tool/analysis.py`
2. `ecg_rr_tool/io.py`
3. `ecg_rr_tool/preprocess.py`
4. `ecg_rr_tool/export.py`
5. `ecg_rr_tool/cli.py`
6. `ecg_rr_tool/gui.py`
7. `ecg_rr_tool/detectors/`
8. `requirements.txt`
9. `pyproject.toml`
10. `.gitignore`
11. `tests/fixtures/bidmc_01_Signals_4000.csv`
12. 输出 CSV 字段；
13. detector 策略；
14. Python 版本要求；
15. GUI 技术栈。

如果发现必须修改上述内容，必须暂停并在 Codex 输出中列为 S0 Owner 决策项。

---

## 7. 文档收敛要求

请重点检查并修正以下文档一致性问题：

1. 所有环境说明统一为 Python 3.11+，不得残留 Python 3.10+ 作为建议环境。
2. CLI 示例不要固定停留在 `outputs/m4_bidmc_01_result.csv`，可统一为：
   - `outputs/example_result.csv`
   - 或 `outputs/m6_cli_smoke.csv`
3. README 当前状态应更新为 M6 / 项目阶段验收。
4. Milestone Plan 应标记 M1-M5 已完成，M6 为当前 / 验收阶段。
5. Runbook 应包含：
   - 依赖安装；
   - CLI 用法；
   - GUI 用法；
   - headless GUI self-test；
   - 输出字段；
   - 常见错误；
   - `outputs/*.csv` 不应提交；
   - 研究 / 工程工具边界。
6. IO Contract 只能做文字澄清，不得改变字段。
7. 风险说明必须明确：
   - 单个 fixture 不能证明总体准确性；
   - 无参考标注，不能计算准确率 / 召回率 / F1；
   - 第三方库检测结果不等于临床有效性证明；
   - 当前 GUI 是最小可视化，不支持缩放、滚动、人工编辑；
   - 当前不做 HRV / PPG IBI / 批量处理。

---

## 8. 验收报告要求

请新增或更新：

```text
docs/07_ACCEPTANCE_REPORT.md
```

该文档至少包含：

1. 项目范围摘要；
2. 当前技术栈；
3. 当前 detector：`wfdb_xqrs`；
4. 当前输入 / 输出契约摘要；
5. CLI 验收结果；
6. GUI / self-test 验收结果；
7. fixture smoke test 结果，至少包括：
   - 输入行数；
   - 输出行数；
   - 估计采样率；
   - R 峰数量；
   - RR 范围；
   - waveform points；
   - marker 数量；
8. 已执行测试命令；
9. 通过 / 未通过结论；
10. 已知限制；
11. 不作为医疗诊断软件的边界说明。

---

## 9. 风险复盘要求

请新增或更新：

```text
docs/08_RISK_REVIEW.md
```

该文档至少包含：

1. S0 决策回顾；
2. S1 阻塞问题状态；
3. S2 技术风险；
4. S3 文档 / 风格问题；
5. 后续建议；
6. 明确不应在当前版本中宣称：
   - 临床准确性；
   - 医疗诊断能力；
   - 对所有 BIDMC 数据泛化有效；
   - 对异常 ECG / 噪声 / 早搏 / 漏搏均可靠。

---

## 10. 验收测试命令

请至少执行并报告以下命令。

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
python -m ecg_rr_tool.gui --help
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m6_cli_smoke.csv
git check-ignore --no-index outputs/m6_cli_smoke.csv
git diff --check
git status --short
```

如果默认 Python 环境缺少依赖，可以使用已安装 M3/M4/M5 正式依赖的 Python 3.11+ 环境执行功能性验收，但必须报告：

1. 默认环境失败原因；
2. 正式依赖环境路径；
3. 正式依赖环境测试结果；
4. 生成的 `outputs/m6_cli_smoke.csv` 是否已删除或未提交。

---

## 11. 通过标准

M6 通过需要满足：

1. 所有核心测试在正式依赖环境通过；
2. CLI smoke test 通过；
3. GUI self-test 通过；
4. 输出字段仍符合 IO Contract；
5. `outputs/*.csv` 未进入 PR；
6. README / Runbook / Milestone Plan / Acceptance Report / Risk Review 内容一致；
7. Python 版本说明统一为 3.11+；
8. 未修改算法逻辑、detector、IO Contract 字段、依赖版本或 GUI 技术栈；
9. 明确保留研究 / 工程工具边界；
10. 不做临床准确性或医疗诊断声明。

---

## 12. 失败时应报告的信息

如果无法完成，请报告：

1. 未满足的通过标准；
2. 失败的测试命令；
3. 关键错误日志；
4. 是否涉及环境、依赖、文档冲突或源码问题；
5. 是否需要 Owner 新增 S0 决策；
6. 建议如何拆分下一轮任务。

---

## 13. Codex 输出摘要要求

完成后请输出：

1. Summary；
2. Changed files；
3. 是否改变算法 / detector / IO Contract / 依赖版本 / GUI 技术栈；
4. Test commands；
5. Test results；
6. Fixture smoke test summary；
7. 文档收敛摘要；
8. 风险复盘摘要；
9. Known limitations；
10. Owner decision needed，如无请写“无”；
11. 未完成事项。

---

## 14. M6 完成记录

状态：已完成。

完成内容：

1. 已新增 `docs/07_ACCEPTANCE_REPORT.md`；
2. 已新增 `docs/08_RISK_REVIEW.md`；
3. 已更新 README、Milestone Plan、Decision Log、Detector Strategy 和 Runbook；
4. 已统一当前建议环境为 Python 3.11+；
5. 已统一 CLI / GUI 示例和 `outputs/*.csv` 运行产物说明；
6. 已记录 fixture smoke test 结果和已知限制；
7. 已确认本项目仍为研究 / 工程分析工具，不作为医疗诊断软件；
8. 已确认 M6 未修改算法逻辑、detector、IO Contract 字段、依赖版本或 GUI 技术栈。

验收结果：

- 默认 Python 3.13.12 环境缺少 `numpy`，功能性命令按预期无法完成；
- 正式依赖环境 `/private/tmp/ecg_m3_deps` 下 `pytest` 通过：`27 passed`；
- CLI smoke test 通过；
- GUI self-test 通过；
- `outputs/m6_cli_smoke.csv` 已删除，未进入 PR；
- `git diff --check` 通过。

下一步占位：如继续迭代，应基于 `docs/08_RISK_REVIEW.md` 的后续建议拆分新任务。
