# 风险分析样例

本文档包含自构造的风险分析条目，用于演示汽车软件需求、测试和缺陷之间的风险追踪关系。风险字段包括 related_function、severity、cause、impact 和 mitigation。

## RISK-AEB-001 低速跟车制动不足

- related_function: AEB
- severity: high
- cause: 前方目标距离估计偏差、TTC 阈值配置过晚或 brake_pedal_status 处理优先级不清晰。
- impact: 在低速跟车场景中，系统可能延迟预警或制动，导致轻微追尾风险增加。
- mitigation: 使用 TC-AEB-LOW-001 覆盖不同相对速度和目标距离；检查 REQ-AEB-001 中驾驶员制动优先级和日志记录要求。

## RISK-AEB-002 雨天误触发导致不必要制动

- related_function: AEB
- severity: medium
- cause: 雨天积水反光、摄像头目标分类不稳定、雷达目标未确认但融合逻辑过度信任视觉输出。
- impact: 车辆可能在无真实障碍物时产生不必要制动，造成驾驶员惊吓或后车追尾风险。
- mitigation: 通过 TC-AEB-RAIN-001 验证 REQ-AEB-003 的多源一致性检查、降级预警和 aeb_degradation_reason 日志。

## RISK-LKA-001 弯道控制边界识别不足

- related_function: LKA
- severity: medium
- cause: 车道线曲率估计异常、steering_torque 接管阈值设置不合理或退出过程缺少扭矩渐退。
- impact: LKA 可能在边界条件下继续输出辅助扭矩，使驾驶员感到控制不自然。
- mitigation: 使用 TC-LKA-CURVE-001 验证 REQ-LKA-003 的退出策略，并检查 SIG-STR-001 steering_torque 的采样稳定性。

## RISK-BMS-001 高温风险告警延迟

- related_function: BMS
- severity: high
- cause: battery_temperature 采样点有效性判断不足、温升速率阈值过宽或热管理请求未及时发出。
- impact: 电池热风险被延迟识别，可能导致功率限制不及时或驾驶员告警不足。
- mitigation: 通过 TC-BMS-HIGH-TEMP-001 验证 REQ-BMS-003 的告警分级、阈值滞回和 diagnostic_event 完整性。

## 分析说明

风险条目用于帮助 Domain Expert Agent 识别工程问题背后的原因、影响和测试补充方向。风险分析不等同于完整 ISO 26262 或 SOTIF 分析，只用于原型级推理链路验证。

