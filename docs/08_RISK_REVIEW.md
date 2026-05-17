# M6 Risk Review

## 1. S0 Decision Review

已确认 S0 决策：

| 决策项 | 当前状态 |
|---|---|
| 项目用途 | 研究 / 工程分析工具，不作为医疗诊断软件 |
| 输入数据 | BIDMC CSV |
| 原始采样率 | 125 Hz |
| 输出采样率 | 50 Hz |
| R 峰检测时机 | 在 125 Hz 原始 ECG 上检测，再映射到 50 Hz 输出行 |
| 主 detector | `wfdb_xqrs` |
| detector fallback | 不保留自研 fallback |
| Python | 3.11+ |
| GUI | Tkinter + Canvas |
| fixture | `tests/fixtures/bidmc_01_Signals_4000.csv` |

M6 未改变以上决策。

## 2. S1 Blocking Issues

当前无阻塞 S1 问题。

已处理：

- 字段名前后空格：读取时使用 `strip()` 后匹配；
- 字段 strip 后重复：返回明确错误；
- 采样率异常：返回明确错误；
- 时间戳非严格递增：返回明确错误；
- 运行产物：`outputs/*.csv` 被忽略，不应进入 PR；
- GUI headless 测试：提供 `python -m ecg_rr_tool.gui --self-test ...`。

## 3. S2 Technical Risks

| 风险 | 说明 | 当前缓解 |
|---|---|---|
| 单个 fixture 代表性不足 | 只验证一个 BIDMC 短片段，不能证明总体准确性 | 文档和测试结果明确标注为 smoke test |
| 无参考标注 | 不能计算准确率、召回率或 F1 | 不输出准确性指标，不做临床级声明 |
| 第三方 detector 风险 | WFDB XQRS 行为依赖第三方库版本和目标环境 | 版本锁定为 `wfdb==4.3.1`，通过 adapter 封装 |
| 无 fallback | detector 失败时没有自研兜底 | 保持 Owner 决策；失败时报告错误 |
| 异常 ECG / 噪声 | 噪声、早搏、漏搏、信号中断未系统性验证 | 后续需引入参考数据和异常场景测试 |
| GUI 最小化 | GUI 不支持缩放、滚动、人工编辑或复杂交互 | 明确 M5 范围，仅用于基本查看 |
| 打包风险 | 未验证桌面端打包和跨平台分发 | 后续单独设置打包里程碑 |

## 4. S3 Documentation / Style Issues

已在 M6 收敛：

- README 当前状态更新为 M6；
- Runbook 环境说明统一为 Python 3.11+；
- CLI 示例统一为非里程碑固定结果路径；
- Milestone Plan 标注 M1-M5 已完成、M6 为当前验收阶段；
- Acceptance Report 与 Risk Review 新增；
- 文档继续保留非医疗诊断边界。

## 5. Follow-up Recommendations

建议后续任务按以下方向拆分，不应混入当前 M6：

1. 引入带参考标注的数据集，建立 R 峰检测准确性评估；
2. 增加噪声、早搏、漏搏、信号中断等异常场景测试；
3. 明确 GUI 后续交互范围，如缩放、滚动、结果查看和人工编辑是否需要；
4. 单独评估桌面端打包方案；
5. 若要输出 HR、HRV 或 PPG IBI，应先更新 IO Contract 并由 Owner 做 S0 决策；
6. 若需要批量处理，应单独设计 CLI / GUI 交互和输出组织。

## 6. Claims Not Allowed In Current Version

当前版本不应宣称：

- 临床准确性；
- 医疗诊断能力；
- 对所有 BIDMC 数据泛化有效；
- 对异常 ECG、噪声、早搏、漏搏均可靠；
- 第三方 detector 结果可替代人工或临床判读；
- 单个 fixture smoke test 可证明算法总体质量。

## 7. Current Boundary

当前版本可描述为：

> 一个用于 BIDMC CSV 的 ECG RR 研究 / 工程分析工具，支持 WFDB XQRS R 峰检测、50 Hz 输出 CSV、最小 CLI 和 Tkinter + Canvas GUI。

当前版本不可描述为医疗诊断软件。
