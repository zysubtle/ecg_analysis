# M3 Codex Task｜WFDB XQRS Detector Adapter 集成与 RR 输出

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

## 1. 当前里程碑

M3：WFDB XQRS Detector Adapter 集成与 RR 输出。

## 2. 已确认 Owner 决策

以下为 Owner 已确认的 S0 决策，不得擅自改变：

1. 采用 **WFDB XQRS** 作为 M3 正式主 detector。
2. 继续保持 **不保留自研 fallback**。
3. 最终运行环境允许 **Python 3.11+**，不强制兼容 Python 3.10。
4. 暂不补充带参考标注的数据集；当前仍只基于 `tests/fixtures/bidmc_01_Signals_4000.csv` 做 smoke test 与工程合理性检查。
5. 本项目仍然只是研究 / 工程分析工具，不是医疗诊断软件。

## 3. 本轮目标

实现正式的 WFDB XQRS detector adapter，并把它接入最小 ECG 分析流程，使项目能够从 BIDMC 示例 CSV 生成符合 IO Contract 的 50 Hz 主输出 CSV。

本轮完成后，应能够：

1. 读取 `tests/fixtures/bidmc_01_Signals_4000.csv`；
2. 对字段名执行 `strip()` 后匹配 `Time [s]`、`II`、`PLETH`；
3. 验证原始采样率约为 125 Hz；
4. 在 125 Hz 原始 ECG 上用 WFDB XQRS 检测 R 峰；
5. 计算 `r_peak_time_s` 与 `rr_ms`；
6. 将 ECG、PPG 和时间戳同步输出为 50 Hz 序列；
7. 将 R 峰时间映射到 50 Hz 输出行；
8. 导出符合 `docs/04_IO_CONTRACT.md` 的 CSV；
9. 通过基于 fixture 的 smoke test。

## 4. 本轮非目标

本轮不做：

1. 不实现完整 GUI；
2. 不做 HR / HRV 指标；
3. 不计算 PPG IBI；
4. 不新增其他主 detector；
5. 不保留自研 fallback；
6. 不做临床准确性声明；
7. 不把单个 CSV 的结果作为总体准确性证明；
8. 不改变已确认输入 / 输出字段；
9. 不做批量处理；
10. 不做桌面端打包。

## 5. 允许修改范围

允许新增或修改：

- `ecg_rr_tool/detectors/base.py`
- `ecg_rr_tool/detectors/factory.py`
- `ecg_rr_tool/detectors/wfdb_detector.py`
- `ecg_rr_tool/cli.py`
- `ecg_rr_tool/` 下必要的数据读取、预处理、分析、导出模块，例如：
  - `ecg_rr_tool/io.py`
  - `ecg_rr_tool/preprocess.py`
  - `ecg_rr_tool/analysis.py`
  - `ecg_rr_tool/export.py`
- `tests/` 下与 M3 相关的测试；
- `requirements.txt`；
- `pyproject.toml`，仅限 Python 版本与必要依赖；
- `docs/01_DECISION_LOG.md`，追加本轮已确认决策；
- `docs/05_DETECTOR_STRATEGY.md`，记录 WFDB XQRS 已被 Owner 选为 M3 主 detector；
- `docs/10_CODEX_NEXT_TASK.md`，任务完成后可更新为当前 M3 完成状态或下一步占位说明。

## 6. 不允许修改范围

未经 Owner 决策，不得修改：

1. `docs/04_IO_CONTRACT.md` 中已确认的输出字段；
2. 输入字段：`Time [s]`、` II` / `II`、` PLETH` / `PLETH`；
3. 原始采样率：125 Hz；
4. 目标输出采样率：50 Hz；
5. R 峰检测时机：必须优先在 125 Hz 原始 ECG 上检测，再映射到 50 Hz 输出；
6. 主 detector：WFDB XQRS；
7. fallback 策略：不保留自研 fallback；
8. 项目用途边界：不得写成医疗诊断软件；
9. 示例 CSV 路径；
10. GUI 范围。

如果发现必须改变上述任何内容，必须暂停并在 Codex 输出中列为 S0 Owner 决策项。

## 7. 依赖要求

1. 正式 runtime 依赖应以 WFDB XQRS 和必要的数值处理依赖为主。
2. M2a 中用于评估的其他候选库不应继续作为正式 runtime 依赖保留，除非明确放入可选评估依赖并说明用途。
3. 允许把 `pyproject.toml` 的 `requires-python` 更新为 `>=3.11`。
4. 若新增依赖，必须写入 `requirements.txt` 和 / 或 `pyproject.toml`。
5. 必须在 Codex 输出中记录关键依赖版本，至少包括：
   - `wfdb`
   - `numpy`
   - `scipy`
   - 其他实际新增依赖。

## 8. Detector adapter 要求

必须通过 adapter 封装 WFDB XQRS。

建议实现：

```text
ecg_rr_tool/detectors/wfdb_detector.py
```

建议 detector 名称统一为：

```text
wfdb_xqrs
```

adapter 必须满足 `ecg_rr_tool.detectors.base.RPeakDetector` 接口，输出统一 `RPeakEvent`。

要求：

1. GUI、CLI、导出模块不得直接调用 WFDB API；
2. 只有 `wfdb_detector.py` 可以直接调用 WFDB XQRS；
3. `detectors/factory.py` 应支持创建 `wfdb_xqrs` detector；
4. adapter 应记录 `detector_name` 和 `detector_version`；
5. adapter 输入为 125 Hz 原始 ECG 序列；
6. adapter 输出的 `r_peak_time_s` 应基于原始时间戳或 125 Hz 采样率换算；
7. `rr_ms` 为相邻 R 峰时间差，单位 ms；
8. 第一个 R 峰的 `rr_ms` 可为 `None`；
9. `quality_flag` 最小可使用 `ok` / `unknown` / `error`。

## 9. 输入处理要求

示例 CSV 固定路径：

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

关键字段：

- 时间戳：`Time [s]`
- ECG：原始字段可能为 ` II`，逻辑字段为 `II`
- PPG：原始字段可能为 ` PLETH`，逻辑字段为 `PLETH`

读取规则：

1. 对 CSV header 执行 `strip()` 后匹配；
2. 如果 `strip()` 后出现重复逻辑字段，应报错，避免静默选错列；
3. 必须校验必要字段存在；
4. 必须校验时间戳单调递增；
5. 必须估计采样率并确认约为 125 Hz；
6. 如果字段缺失、采样率异常或时间戳异常，应返回清晰错误信息。

## 10. 50 Hz 输出与 R 峰映射要求

输出 CSV 必须按 50 Hz 采样点逐行组织。

输出字段必须包含：

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

处理要求：

1. ECG 与 PPG 从 125 Hz 同步降采样到 50 Hz；
2. 推荐使用 `scipy.signal.resample_poly(up=2, down=5)` 处理 ECG 与 PPG；
3. 50 Hz 时间戳应与输出序列长度一致；
4. 推荐使用 `time_s_50hz = time_start + np.arange(n_out) / 50.0` 生成 50 Hz 时间戳，避免对时间戳做滤波引入偏移；
5. R 峰检测仍在 125 Hz 原始 ECG 上完成；
6. 将 `r_peak_time_s` 映射到 50 Hz 输出行，建议：

```text
mapped_index_50hz = round((r_peak_time_s - time_start) * 50.0)
```

7. `r_peak_sample_index` 在主输出 CSV 中表示映射后的 50 Hz 输出行索引；
8. 非 R 峰行的 R 峰 / RR / detector / quality 字段应为空；
9. R 峰行应填写 `r_peak_sample_index`、`r_peak_time_s`、`rr_ms`、`detector_name`、`quality_flag`；
10. 不要新增 `hr_bpm` 或 HRV 字段。

## 11. CLI 要求

本轮可以实现最小 CLI 分析入口，用于 smoke test 和导出。

建议命令形式：

```bash
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m3_bidmc_01_result.csv
```

要求：

1. 保留 `python -m ecg_rr_tool.cli --version`；
2. 输入 CSV 与输出 CSV 使用仓库相对路径；
3. 默认 detector 为 `wfdb_xqrs`；
4. CLI 运行后打印：
   - 输入行数；
   - 输出行数；
   - 估计原始采样率；
   - detector 名称；
   - 检测到的 R 峰数量；
   - RR 合理性摘要；
   - 输出文件路径；
5. 如果输出目录不存在，可以自动创建；
6. CLI 不输出医疗诊断结论。

## 12. 测试要求

至少新增或更新以下测试：

1. detector factory 能创建 `wfdb_xqrs`；
2. WFDB adapter 在 fixture ECG 上能输出 R 峰事件；
3. R 峰数量在 smoke test 合理范围内，建议 `45 <= n_peaks <= 55`；
4. RR 范围基本合理，建议非空 RR 均在 `300-2000 ms` 内；
5. 分析流程能生成 50 Hz 输出 CSV；
6. 输出 CSV 字段完整且顺序合理；
7. fixture 4000 行输入应生成约 1600 行 50 Hz 输出；
8. R 峰行能填充 `r_peak_sample_index`、`r_peak_time_s`、`rr_ms`、`detector_name`、`quality_flag`；
9. CLI smoke test 能运行并生成输出文件；
10. 缺失必要字段时应有清晰错误。

## 13. 建议测试命令

请至少执行并报告以下命令。可根据项目实际结构补充命令，但不能省略核心 smoke test。

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m3_bidmc_01_result.csv
git diff --check
```

如果默认 Python 环境缺少依赖，应说明实际使用的 Python 解释器、依赖安装位置和完整测试命令。

## 14. 通过标准

M3 通过需要满足：

1. WFDB XQRS 已通过正式 adapter 封装；
2. GUI / CLI / 导出模块没有直接散落调用 WFDB API；
3. factory 能创建 `wfdb_xqrs`；
4. 依赖文件记录正式依赖；
5. 不再把全部 M2a 候选库都作为正式 runtime 依赖；
6. 示例 CSV 使用仓库内相对路径；
7. 能生成符合 IO Contract 的 50 Hz 输出 CSV；
8. R 峰数量、RR 范围、输出行数、字段完整性通过 smoke test；
9. 未新增 HR、HRV、医疗诊断字段；
10. 未改变已确认输入 / 输出字段；
11. 文档记录 Owner 已确认的 detector 决策；
12. 测试命令真实执行并通过，或清楚说明失败原因。

## 15. 失败时应报告的信息

如果无法完成，请报告：

1. 未满足的通过标准；
2. 失败的测试命令；
3. 关键错误日志；
4. 是否是依赖安装、Python 版本、WFDB API、数据字段、采样率或实现问题；
5. 是否需要 Owner 新增 S0 决策；
6. 建议如何拆分下一轮任务。

## 16. Codex 输出摘要要求

完成后请输出：

1. Summary；
2. Changed files；
3. Dependency changes and versions；
4. Detector adapter location；
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

## 17. M3 完成记录

状态：已完成。

完成内容：

1. 已实现 `wfdb_xqrs` 正式 detector adapter；
2. 已实现 BIDMC CSV 读取、字段 `strip()` 匹配、采样率校验、50 Hz 同步降采样、R 峰映射和 CSV 导出；
3. 已实现最小 CLI 分析入口；
4. 已将正式 runtime 依赖收敛为 WFDB XQRS 相关依赖；
5. 已新增 M3 smoke tests；
6. 已基于 `tests/fixtures/bidmc_01_Signals_4000.csv` 生成 `outputs/m3_bidmc_01_result.csv`。

下一步占位：M4 可继续完善 CLI 与导出结果体验、错误处理和回归测试。
