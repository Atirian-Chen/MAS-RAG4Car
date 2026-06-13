# BMS 电池管理系统需求样例

本文档是自构造的 BMS（Battery Management System，电池管理系统）需求样例，用于验证 AutoDev Multi-Agent RAG 在电池安全、告警策略、信号定义和测试追踪场景下的表现。内容仅用于方法原型，不代表真实电池包设计。

## 功能背景

BMS 负责监控电芯电压、电流、电池温度、SOC、绝缘状态和热管理状态。对于汽车软件开发而言，BMS 需求不仅描述数据采集，还需要说明阈值判断、告警分级、热失控风险控制和诊断记录。高温、电压异常和电流突变通常需要与整车控制器、热管理系统和仪表告警进行协同。

## 需求条目

### REQ-BMS-001 电池温度监控与采样

BMS 应周期性采集 battery_temperature，并对每个温度采样点执行有效性检查。SIG-BAT-001 battery_temperature 的 sample_rate 不应低于热管理控制所需频率。若单点温度异常但相邻采样点正常，系统应标记传感器可疑状态；若多个采样点持续升高，则应进入高温风险评估流程。该需求 priority 为 P1，safety_relevance 为 high。

### REQ-BMS-002 电压电流一致性检查

BMS 应对电芯电压、电池包电流和 SOC 变化趋势进行一致性检查。当出现电压快速下降但电流信号未同步变化时，应记录诊断事件并触发数据完整性检查。该需求用于支持故障定位，避免单一信号错误导致错误的续航估算或热风险判断。

### REQ-BMS-003 热失控风险告警策略

当 battery_temperature 超过高温阈值并持续上升，或温升速率超过风险门限时，BMS 应发出分级告警。轻微异常可触发热管理增强请求，严重异常应触发仪表告警并限制功率输出。该需求与 TC-BMS-HIGH-TEMP-001、RISK-BMS-001 和 BUG-BMS-001 相关，需要验证告警时序、阈值滞回和日志完整性。

## 接口与约束

BMS 输入包括 SIG-BAT-001 battery_temperature、电芯电压列表、电池包电流、SOC、冷却回路状态和绝缘监测状态。输出包括 battery_warning_level、thermal_management_request、power_limit_request 和 diagnostic_event。需求不实现热模型，只要求软件在样例数据下能够形成可解释的风险判断。

