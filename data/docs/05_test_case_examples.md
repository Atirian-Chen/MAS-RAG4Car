# 测试用例样例

本文档包含自构造的汽车软件功能测试用例，用于验证需求与测试之间的 traceability。每条测试用例包含 scenario、precondition、steps、expected_result 和 verified_requirement，便于 RAG 系统生成测试补充建议。

## TC-AEB-LOW-001 低速跟车制动预警

- scenario: AEB 低速跟车场景，前车突然减速。
- precondition: vehicle_speed 为 30 km/h，前方目标识别稳定，brake_pedal_status 为 released，道路干燥。
- steps: 1. 设置前车相对距离逐步减小；2. 注入前车减速度；3. 记录 TTC、warning_request 和 brake_request；4. 检查 event_log_id。
- expected_result: 系统先进入预警状态，TTC 达到阈值后触发分级制动；若驾驶员未制动，AEB 自动制动请求应被记录。
- verified_requirement: REQ-AEB-001

## TC-AEB-RAIN-001 雨天反光误触发抑制

- scenario: 雨天低速道路存在积水反光，摄像头目标分类短时波动。
- precondition: vehicle_speed 为 25 km/h，雷达未确认稳定障碍物，brake_pedal_status 为 released，摄像头置信度波动。
- steps: 1. 注入雨天反光目标；2. 让摄像头输出在障碍物和非障碍物之间变化；3. 观察 AEB 是否直接强制制动；4. 检查 aeb_degradation_reason。
- expected_result: 系统不应仅依赖单一摄像头结果触发强制制动，应进入降级预警或保持监控，并记录一致性不足原因。
- verified_requirement: REQ-AEB-003

## TC-LKA-CURVE-001 高速弯道边界退出

- scenario: LKA 在高速弯道中遇到车道线置信度下降。
- precondition: vehicle_speed 为 90 km/h，左右车道线初始可识别，steering_torque 小于接管阈值。
- steps: 1. 提高道路曲率；2. 降低一侧车道线置信度；3. 注入驾驶员轻微接管扭矩；4. 记录 steering_torque_request。
- expected_result: LKA 应限制扭矩请求，在车道线质量不足或驾驶员接管时执行扭矩渐退并退出。
- verified_requirement: REQ-LKA-003

## TC-BMS-HIGH-TEMP-001 电池高温告警

- scenario: 电池温度持续升高并超过高温阈值。
- precondition: battery_temperature 初始为 42 degC，冷却回路可用，电池包电流处于中等负载。
- steps: 1. 按设定斜率提高 battery_temperature；2. 注入多个采样点同步升高；3. 观察 battery_warning_level；4. 检查 thermal_management_request 和 diagnostic_event。
- expected_result: BMS 应先触发热管理增强请求，严重高温时提高告警等级并限制功率输出；日志应包含温度值、温升速率和阈值判断。
- verified_requirement: REQ-BMS-003

