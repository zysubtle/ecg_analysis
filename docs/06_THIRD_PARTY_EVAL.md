# Third-party R-peak Detector Evaluation v0.1

## 1. Scope

本文件记录 M2a：第三方 ECG R 峰 / QRS 检测库评估与选型。

本轮只做研究 / 工程用途的 smoke test，不做完整 GUI、完整 CLI 分析流程、正式 detector adapter 集成、临床级准确性声明，也不把单个 CSV 结果作为总体准确性证明。

评估脚本：

```text
tools/evaluate_detectors.py
```

测试数据固定使用仓库内相对路径：

```text
tests/fixtures/bidmc_01_Signals_4000.csv
```

## 2. Environment And Install

实际评估环境：

| 项目 | 值 |
|---|---|
| Python | 3.12.13 |
| 安装位置 | `/private/tmp/ecg_m2a_deps` |
| fixture 样本数 | 4000 |
| 估计采样率 | 125.000000 Hz |
| RR 基本合理范围检查 | 300-2000 ms |

安装命令：

```bash
/Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 -m pip install --target /private/tmp/ecg_m2a_deps neurokit2 wfdb biosppy sleepecg heartpy scipy
```

安装结果：成功。pip 输出包含目标目录已有同名包的 warning，但所有候选包最终安装成功。

依赖已记录在 `requirements.txt`。注意：本轮解析到的 `numpy==2.4.5` 和 `scipy==1.17.1` 的包元数据要求 Python >=3.11；若 Owner 后续要求严格支持 Python 3.10 运行环境，需要在 M3 前重新锁定兼容 Python 3.10 的版本组合。

## 3. Candidate Summary

| 候选方案 | 版本 | R 峰 / QRS 支持 | 125 Hz 输入 | CSV 适配 | License 元数据 | 安装情况 | 桌面端打包风险 | 维护风险 |
|---|---:|---|---|---|---|---|---|---|
| NeuroKit2 | 0.2.13 | 支持 `ecg_peaks` | 可直接传入采样率 | 容易，输入数组即可 | MIT | 成功 | 依赖较多：numpy/scipy/pandas/matplotlib/scikit-learn | 中，项目活跃但范围较大 |
| WFDB XQRS | 4.3.1 | 支持 `processing.xqrs_detect` | 可直接传入 `fs` | 容易，输入数组即可 | MIT | 成功 | 中，依赖 scipy/numpy/pandas/aiohttp/soundfile | 低到中，PhysioNet/WFDB 生态成熟 |
| BioSPPy | 2.2.4 | 支持 `signals.ecg.ecg` 输出 `rpeaks` | 可直接传入采样率 | 容易，输入数组即可 | BSD 3-clause | 成功 | 高，安装拉入 OpenCV/h5py，临时依赖目录中 `cv2` 约 119M | 中，通用生物信号库 |
| SleepECG | 0.5.9 | 支持 `detect_heartbeats` | 可直接传入 `fs` | 容易，输入数组即可 | BSD 3-Clause | 成功 | 中，包小但有平台 wheel / native backend 风险 | 中，项目较专注但生态小于 WFDB |
| HeartPy | 1.2.7 | 可做峰检测，但不是 ECG 专用 QRS detector | 可直接传入采样率 | 容易，输入数组即可 | GPL classifier / metadata license UNKNOWN | 成功 | 中，依赖 scipy/numpy/matplotlib | 中到高，license 与 ECG 专用性均需注意 |
| SciPy find_peaks baseline | scipy 1.17.1 / numpy 2.4.5 | 可组合实现峰检测，不是现成 ECG detector | 可适配 | 容易 | SciPy BSD / NumPy BSD-3-Clause expression | 成功 | 中，SciPy wheel 约 97M，NumPy 约 33M | 高，若作为主方案等同自研调参算法 |

## 4. Smoke Test Results

运行命令：

```bash
env PYTHONPATH=/private/tmp/ecg_m2a_deps /Users/lzy/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 tools/evaluate_detectors.py tests/fixtures/bidmc_01_Signals_4000.csv
```

结果摘要：

| 候选方案 | 状态 | R 峰数量 | 前 8 个 R 峰时间 s | RR ms 摘要 | RR 越界数 | IO Contract 映射 | quality_flag |
|---|---|---:|---|---|---:|---|---|
| NeuroKit2 | ok | 50 | 0.400, 1.032, 1.672, 2.320, 2.960, 3.592, 4.240, 4.880 | count=49, min=624, median=640, max=648 | 0 | 可映射 | ok |
| WFDB XQRS | ok | 50 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 | count=49, min=624, median=640, max=656 | 0 | 可映射 | ok |
| BioSPPy | ok | 49 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 | count=48, min=624, median=640, max=648 | 0 | 可映射 | ok |
| SleepECG | ok | 50 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 | count=49, min=624, median=640, max=656 | 0 | 可映射 | ok |
| HeartPy | ok | 49 | 0.392, 1.032, 1.672, 2.320, 2.960, 3.592, 4.240, 4.880 | count=48, min=224, median=640, max=1928 | 1 | 可映射 | unknown |
| SciPy find_peaks baseline | ok | 50 | 0.400, 1.032, 1.680, 2.320, 2.960, 3.600, 4.248, 4.888 | count=49, min=624, median=640, max=656 | 0 | 可映射 | ok |

无法安装或无法运行的库：本轮安装环境中无。脚本支持缺失依赖时报告 `import_failed`，以便其他环境复现时定位。

## 5. IO Contract Mapping

所有成功运行候选都能转换为统一 detector 输出：

| IO 字段 | 映射方式 |
|---|---|
| `r_peak_sample_index` | 第三方 detector 返回的原始 125 Hz 样本索引 |
| `r_peak_time_s` | 使用 fixture 时间戳按样本索引映射 |
| `rr_ms` | 相邻 `r_peak_time_s` 差值乘以 1000 |
| `detector_name` | 候选库 / 方法名 |
| `quality_flag` | smoke test 中使用 `ok` / `unknown` / `error` |

后续 M3 正式集成必须通过 adapter 层封装，不得在 GUI、CLI 或导出模块中直接调用第三方库 API。

## 6. Noise And Abnormal Rhythm Notes

本轮 fixture 较短且没有参考标注，不能评估总体准确性，也不能覆盖噪声、漏搏、早搏、信号中断等场景。

候选能力与限制：

| 候选方案 | 能力与限制 |
|---|---|
| NeuroKit2 | ECG 工具链完整，包含预处理和多种 ECG 方法；依赖栈大，具体异常场景需要后续数据验证。 |
| WFDB XQRS | 面向 ECG/QRS 的经典处理接口，适合数组输入；异常节律和噪声下表现需要参考标注验证。 |
| BioSPPy | ECG pipeline 完整，但本 fixture 少检测 1 个峰，且依赖较重。 |
| SleepECG | 专注心搏检测，smoke 结果与 WFDB 接近；native backend / wheel 支持需在目标平台验证。 |
| HeartPy | 峰检测能运行，但不是 ECG 专用 QRS detector，本轮出现 1 个 RR 越界，不建议作为主 detector。 |
| SciPy find_peaks baseline | 可作为工程对照，但需要自定义滤波、阈值和质量策略；若作为最终主方案，实际等同自研算法路线。 |

## 7. Recommendation

推荐提交 Owner 决策的主方案：**WFDB XQRS**。

理由：

- 本轮在 125 Hz fixture 上检测 50 个 R 峰，RR 全部落在 300-2000 ms 基本范围内；
- 输出是样本索引，最容易映射到当前 IO Contract；
- license 元数据为 MIT；
- WFDB / PhysioNet 生态与 ECG 数据处理更贴近；
- 相比 NeuroKit2，业务语义更聚焦 QRS/R 峰检测；
- 相比 BioSPPy，桌面端依赖负担更低；
- 相比 SleepECG，生态成熟度和可追溯性更强；
- 相比 HeartPy 和 SciPy baseline，更符合“第三方 ECG/QRS detector”路线。

可作为 Owner 对比的替代方案：**SleepECG**。它的 smoke 结果同样通过，依赖体积较小；主要风险是平台 wheel / native backend 和生态成熟度。

不建议作为主 detector：

- HeartPy：不是 ECG 专用 QRS detector，本轮有 RR 越界；
- SciPy find_peaks baseline：会把项目推向自研检测逻辑，不符合当前“不默认从零自研”的策略；
- BioSPPy：能运行但依赖明显偏重，本轮 R 峰数量也少 1 个；
- NeuroKit2：结果可用，但依赖栈较宽，若只需要 QRS/R 峰检测可能偏重。

## 8. No-Fallback Risk

Owner 已确认不保留自研 fallback。该策略下的风险：

1. 如果最终选定库在目标桌面平台无法安装或打包，M3/M5 不应静默切换到自研算法，只能报告安装 / 运行错误或回到 Owner 决策；
2. 如果最终选定库在噪声、漏搏、早搏、信号中断等场景表现不稳定，当前没有自研 fallback 可兜底；
3. 输出质量标志需要由 adapter 明确记录，不能把单个 detector 的失败隐藏为正常结果；
4. 依赖版本必须锁定并在发布前做目标平台验证；
5. Python 3.10 支持需要单独确认依赖版本组合，不能因为 M2a 在 Python 3.12 成功就默认覆盖所有环境。

## 9. Owner Decision Needed

以下为 S0 决策项，Codex 不应擅自决定：

1. 是否采用 **WFDB XQRS** 作为 M3 正式主 detector；
2. 如果不采用 WFDB，是否选择 SleepECG / NeuroKit2 / 其他候选作为主 detector；
3. 是否维持“不保留自研 fallback”策略；
4. 是否要求最终运行环境严格支持 Python 3.10，还是允许使用 Python 3.11+ 版本组合；
5. 是否需要新增更多带参考标注的数据集作为 M3/M6 准确性或回归评估基础。

## 10. Known Limitations

- 本轮只使用 `tests/fixtures/bidmc_01_Signals_4000.csv` 一个短片段；
- 没有人工或公开参考 R 峰标注，因此不能计算准确率、召回率或 F1；
- RR 合理性检查只是工程 smoke check，不是准确性证明；
- 未做 GUI、CLI 正式流程或 adapter 集成；
- 未做 Windows/Linux/macOS 打包验证；
- 未做噪声、异常节律、信号中断的系统性测试。
