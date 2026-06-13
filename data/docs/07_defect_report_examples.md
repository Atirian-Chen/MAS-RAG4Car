# 缺陷报告样例

本文档包含自构造的缺陷报告，用于验证 RAG 系统在问题定位、相关需求追踪和建议验证方面的能力。缺陷字段包括 symptom、related_requirement、suspected_root_cause 和 suggested_validation。

## BUG-AEB-001 雨天低速无障碍物误触发

- symptom: 雨天低速通过积水路面时，前方无真实障碍物，但 AEB 出现短促制动请求，event_log_id 中记录摄像头目标置信度波动。
- related_requirement: REQ-AEB-003
- suspected_root_cause: 视觉目标分类短时误判被融合逻辑放大，雷达目标未确认时仍进入制动决策；aeb_degradation_reason 记录不完整，导致复现分析困难。
- suggested_validation: 回放 TC-AEB-RAIN-001，检查 SIG-VSP-001 vehicle_speed、SIG-BRK-001 brake_pedal_status、摄像头置信度、雷达目标确认状态和降级原因日志。

## BUG-LKA-001 弯道中驾驶员接管后扭矩退出不平顺

- symptom: 高速弯道中驾驶员轻微施加 steering_torque 后，LKA 仍维持短时间辅助扭矩，驾驶员感知到方向盘阻尼变化。
- related_requirement: REQ-LKA-003
- suspected_root_cause: 驾驶员接管阈值存在滞后，扭矩渐退参数与道路曲率变化耦合不足。
- suggested_validation: 执行 TC-LKA-CURVE-001，重点观察 SIG-STR-001 steering_torque、steering_torque_request 和退出状态日志。

## BUG-BMS-001 高温告警日志缺少温升速率

- symptom: battery_temperature 持续升高后系统触发告警，但 diagnostic_event 中只有温度绝对值，缺少温升速率和阈值判断信息。
- related_requirement: REQ-BMS-003
- suspected_root_cause: 告警日志字段设计不完整，或者温升速率计算模块未向诊断事件传递结果。
- suggested_validation: 执行 TC-BMS-HIGH-TEMP-001，检查 SIG-BAT-001 battery_temperature、battery_warning_level、thermal_management_request 和 diagnostic_event 字段完整性。

## 缺陷闭环说明

缺陷分析应回到需求和测试，不应只停留在现象描述。对于本原型，Defect Agent 的目标是从缺陷文本中提取相关需求、信号和验证用例，并给出基于样例文档的可追踪排查路径。

