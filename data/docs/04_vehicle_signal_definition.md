# 车辆信号定义样例

本文档定义 AutoDev Multi-Agent RAG 原型使用的车辆信号样例。信号定义用于连接 Requirement、Function、TestCase、Risk 和 Defect，帮助检索器在回答中给出可追踪依据。所有信号均为自构造示例。

## 信号列表

### SIG-VSP-001 vehicle_speed

- source: Vehicle Dynamics Controller
- target: AEB, LKA, BMS diagnostic context
- unit: km/h
- sample_rate: 50 Hz
- description: 表示整车当前速度。AEB 使用该信号判断低速跟车和静止障碍物场景是否满足触发范围；LKA 使用该信号判断车道保持辅助是否处于可用速度区间；BMS 可在诊断日志中记录速度上下文，辅助分析高温或功率限制事件。

### SIG-BRK-001 brake_pedal_status

- source: Brake System Controller
- target: AEB
- unit: enum released / pressed / strong_pressed
- sample_rate: 50 Hz
- description: 表示驾驶员制动踏板状态。REQ-AEB-001 要求系统在驾驶员明显制动时降低自动制动触发优先级，但仍保留碰撞风险日志。该信号也用于分析 BUG-AEB-001 中误触发是否发生在驾驶员未制动状态。

### SIG-STR-001 steering_torque

- source: Electric Power Steering
- target: LKA
- unit: Nm
- sample_rate: 100 Hz
- description: 表示驾驶员或系统在方向盘上的扭矩输入。REQ-LKA-002 和 REQ-LKA-003 使用该信号判断扭矩辅助限制、驾驶员接管和退出控制条件。若 steering_torque 持续超过阈值，LKA 应执行扭矩渐退并退出。

### SIG-BAT-001 battery_temperature

- source: Battery Sensor Module
- target: BMS
- unit: degC
- sample_rate: 10 Hz
- description: 表示电池包内部采样点温度。REQ-BMS-001 要求 BMS 对该信号进行有效性检查；REQ-BMS-003 要求结合温度绝对值和温升速率进行热失控风险告警。TC-BMS-HIGH-TEMP-001 用该信号验证高温告警策略。

## 使用原则

信号定义不替代接口控制文档，只用于样例级知识工程。检索和报告生成时，信号可作为 evidence 连接需求、测试与缺陷分析。例如 AEB 雨天误触发分析通常会同时引用 SIG-VSP-001、SIG-BRK-001 和 REQ-AEB-003。

