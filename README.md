# 桌面端 ECG 分析算法项目

本项目是一个研究 / 工程分析工具，用于从 BIDMC CSV 数据中读取 ECG 与 PPG，对 ECG、PPG 和时间戳同步降采样，并基于 ECG 检测 R 峰、输出 RR。

> 注意：本项目不作为医疗诊断软件，不输出医疗诊断结论。第三方库运行结果、R 峰检测结果、RR 结果仅用于工程分析与验证。

## 当前状态

当前包已推进到 **M5：最小 GUI 与波形可视化**，包含：

- 项目文档；
- IO Contract；
- detector 策略说明；
- Codex / Agent 协作规则；
- WFDB XQRS detector adapter；
- BIDMC CSV 读取、125 Hz 校验、50 Hz 输出和 RR 导出流程；
- 最小 CLI；
- Tkinter + Canvas 最小 GUI；
- 示例 CSV fixture。

当前包不做 HR / HRV、PPG IBI、批量处理、复杂 GUI 交互、人工编辑 R 峰或临床准确性声明。

## CLI 示例

```bash
python -m ecg_rr_tool.cli --version
python -m ecg_rr_tool.cli --about
python -m ecg_rr_tool.cli tests/fixtures/bidmc_01_Signals_4000.csv outputs/m4_bidmc_01_result.csv
```

`outputs/` 是运行产物目录，导出的 CSV 不应提交。

## GUI 示例

```bash
python -m ecg_rr_tool.gui
python -m ecg_rr_tool.gui --self-test tests/fixtures/bidmc_01_Signals_4000.csv
```

GUI 使用 Tkinter + Canvas，可选择输入 CSV、填写输出路径、运行分析、显示 50 Hz ECG 波形并标记 R 峰。`--self-test` 不创建窗口，适合无显示环境 smoke test。

## 示例数据

示例 CSV 已放置在：

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

关键字段：

- `Time [s]`：时间戳，单位秒；
- ` II`：ECG 导联字段，注意字段名前有空格；
- ` PLETH`：PPG 字段，注意字段名前有空格。

代码读取时应对列名执行 `strip()` 后匹配。

## 建议下一步

将本项目包解压并放入 GitHub 仓库后，让 Codex 执行：

```text
请读取 docs/10_CODEX_NEXT_TASK.md，并严格执行。
```

当前 `docs/10_CODEX_NEXT_TASK.md` 对应最新里程碑任务。
