# 可观测与性能

## 1. 指标分类

| 类别 | 指标示例 |
|------|----------|
| API | http_request_duration_seconds |
| 任务 | task_queue_depth / task_duration |
| 模型 | emotion_infer_latency_ms |
| 实时 | ws_active_connections / ws_msg_rate |
| 报告 | report_section_latency_seconds |
| 代码 | code_analysis_stage_time |

## 2. 日志结构

```json
{
 "level":"INFO",
 "ts":"2025-08-27T10:00:00Z",
 "msg":"report_section_ready",
 "task_id":"rpt_01H...",
 "section":"intro",
 "trace_id":"trc_..."
}
```

## 3. 链路追踪

Span 命名规范：

- http.server
- service.chat.llm_call
- service.report.section.build
- ai.emotion.infer

## 4. Dashboard 建议

| 板块 | 图表 |
|------|------|
| API 延迟 | P50/P95/P99 |
| WS | 活跃连接 & 断线率 |
| 模型 | 推断延迟直方图 |
| 队列 | Depth / Fail Rate |
| Miyu | 访问成功/失败比 |

## 5. 性能预算

| 场景 | 预算 |
|------|------|
| Chat 首包 | <150ms 服务端处理 |
| Emotion 推断 | <80ms |
| 报告单段 | <4s |
| 代码 ≤1k 行 | <6s |
| WS 重连恢复 | <2s |

## 6. 压测

k6 样例：

```js
import http from 'k6/http';
export default function() {
  http.post('http://localhost:8000/api/v1/chat/session/sid/message',
    JSON.stringify({content:"你好"}), { headers: {'Content-Type':'application/json'} });
}
```

## 7. 性能优化策略

| 模块 | 策略 |
|------|------|
| Chat | 上下文裁剪 + Token 缓存 |
| Emotion | Batch + ONNX 量化 |
| Report | 并行 Section + 预取资源 |
| Code | Hash 缓存 / 分阶段 |
| 前端 | 分包 / 代码拆分 / 虚拟列表 |

## 8. 错误率监控

| 指标 | 阈值 |
|------|------|
| 5xx rate | <1% |
| WS reconnect fail | <2% |
| Section fail | <3% |
