# 实时与事件系统

## 1. 目标

统一多源数据（chat / report / learning / code / emotion）实时合成，保证：

- 延迟低
- 订阅粒度细
- 客户端降级能力

## 2. 通道

| 协议 | 用途 | 降级 |
|------|------|------|
| WebSocket | 多主题聚合 | SSE/轮询 |
| SSE | Chat 流式 (备选) | 轮询 |
| HTTP 轮询 | 异步任务状态 | 默认 fallback |

## 3. 订阅语法

```
wss://.../ws?topics=chat:sess_123,report:rpt_456,emotion:user
```

## 4. 消息 Envelope

```json
{
 "type": "event|stream|pong",
 "channel": "report.section.ready",
 "payload": {...},
 "ts": 1735345345,
 "trace_id": "trc_..."
}
```

## 5. 客户端合成策略

| 类别 | 合并策略 |
|------|----------|
| Chat token | 直接 append |
| Section ready | 占位符替换 |
| Graph diff | 对局部节点 patch |
| Emotion | 仅变化幅度>阈值发布 |
| Code stage | 进度条 + 子图延迟加载 |

## 6. 重连/补偿

- 心跳：每 30s ping/pong
- 断线：5s,10s,20s 指数退避
- Replay：使用 `last_event_id` 获取缺失事件（未来扩展）

## 7. 事件发布接口（后端）

`publish_event(event_type, data, actor=None, trace_id=None)`

## 8. Schema 管理

- 后端 `core/events/schema_registry.py`
- 可选 JSON Schema 校验（dev 模式开启）

## 9. 监控指标

| 指标 | 描述 |
|------|------|
| ws_active_connections | 当前连接数 |
| ws_message_rate | 每秒消息数 |
| event_processing_latency_ms | 事件队列延迟 |

## 10. 降级策略

| 条件 | 行为 |
|------|------|
| WS 建立失败 3 次 | 切换 SSE |
| SSE 超时 | 简化轮询 |
| 事件风暴 | 客户端本地节流（250ms 合并） |

## 11. 安全

- 鉴权：初始连接携带 Access Token
- 私密主题：需 PST 验证
- 订阅越权：直接关闭连接（1008 code）
