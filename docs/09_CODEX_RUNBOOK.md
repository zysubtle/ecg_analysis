# Codex Runbook v0.1

## 默认执行指令

Owner 给 Codex 的默认指令：

```text
请读取 docs/10_CODEX_NEXT_TASK.md，并严格执行。
```

## 环境建议

建议使用 Python 3.11+。

初始化环境示例：

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

如果当前任务允许安装第三方库，必须：

1. 将依赖写入 `requirements.txt` 或 `pyproject.toml`；
2. 在任务输出中记录实际版本；
3. 说明安装是否成功；
4. 如果安装失败，说明错误原因和替代建议。

## 当前 fixture

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

CSV 关键字段：

- `Time [s]`
- ` II`
- ` PLETH`

读取时应对字段名执行 `strip()` 后匹配。

## 依赖安装

建议使用 Python 3.11+。

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
python -m pip install pytest
```

当前正式 runtime detector 为 `wfdb_xqrs`，依赖版本记录在 `requirements.txt` / `pyproject.toml`。

## CLI 使用

版本检查：

```bash
python -m ecg_rr_tool.cli --version
```

项目用途边界说明：

```bash
python -m ecg_rr_tool.cli --about
```

分析 fixture 并导出 CSV：

```bash
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/example_result.csv
```

成功运行后 CLI 输出 key-value summary，包括输入行数、输出行数、估计采样率、detector 名称和版本、R 峰数量、RR 摘要和输出路径。

输出 CSV 字段固定为：

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

`outputs/` 是运行产物目录，`outputs/*.csv` 不应提交到 PR。

常见错误：

- `Input CSV does not exist`：输入路径不存在；
- `Missing required columns after strip()`：缺少 `Time [s]`、`II` 或 `PLETH`；
- `Duplicate CSV columns after strip()`：字段名去除空格后重复；
- `Timestamps must be strictly increasing`：时间戳不是严格递增；
- `Estimated sampling rate must be approximately 125 Hz`：输入采样率不符合当前契约；
- `Unknown detector`：传入了未支持的 detector 名称。

本项目仅为研究 / 工程分析工具，不作为医疗诊断软件，不输出医疗诊断结论。

## GUI 使用

M5 最小 GUI 使用 Tkinter + Canvas，不新增 PySide6、matplotlib 或其他 GUI / 绘图库依赖。

启动 GUI：

```bash
python -m ecg_rr_tool.gui
```

GUI 支持：

- 选择 BIDMC CSV；
- 填写或选择输出 CSV；
- 调用现有 `analyze_csv()` / `write_output_csv()` 流程；
- 显示 50 Hz ECG 波形；
- 标记 R 峰；
- 显示基础分析摘要；
- 导出符合 IO Contract 的 CSV。

无显示环境自检：

```bash
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
```

GUI 与 self-test 仍只作为研究 / 工程分析工具使用，不作为医疗诊断软件。GUI 不直接调用 WFDB API，正式 detector 仍通过 adapter 和 analysis 层使用。

## M1 最小测试命令

```bash
python -m pytest
python -m ecg_rr_tool.cli --version
```

M1 不要求完整算法运行。

## M6 验收命令

默认环境若未安装正式 runtime 依赖，功能性验收应在 Python 3.11+ 且已安装 `requirements.txt` / `pyproject.toml` 依赖的环境中执行。

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

执行 smoke test 后应删除 `outputs/m6_cli_smoke.csv`，不得提交运行产物。

## 后续算法类任务的测试要求

如果任务涉及算法处理、CLI、GUI、第三方库集成或导出功能，且仓库中已有示例 CSV，则验收标准必须包含基于该示例 CSV 的测试。

测试命令必须使用仓库内相对路径，例如：

```bash
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/result.csv
```

不得使用：

- “使用 sources 中的 CSV 文件”；
- “使用用户上传的 CSV 文件”；
- “使用聊天附件中的 CSV 文件”。
