# 架构导览（Walkthrough）

本文件将核心架构与代码结构映射，帮助你从“概念 → 代码”快速定位。

## 1. 分层
| 层 | 位置 | 核心 |
|----|------|------|
| 体验呈现 | frontend/src | UI、动画、语义主题 |
| 体验编排 | frontend/src/context + hooks | Emotion → Theme、RealtimeComposer |
| 领域服务 | backend/app/services | Chat / Miyu / Learning / Report / Code |
| AI 管线 | backend/app/core/ai | 情感、推荐、报告组合 |
| 异步任务 | backend/app/core/tasks + worker | Celery 队列执行 |
| 数据访问 | backend/app/models | Django ORM / Graph / Vector 调用 |
| 事件 & 实时 | backend/app/websocket + EventBus | WS, Kafka/NATS(抽象) |
| 安全合规 | backend/app/auth + privacy | 鉴权、加密、留存策略 |
| 可观测 | backend/app/instrumentation | logging/metrics/tracing |

## 2. 目录与职责映射
```
backend/app/
  api/v1/          # DRF 视图 / 路由
  services/        # 业务逻辑封装
  models/          # 数据模型
  core/ai/         # 模型封装、推理接口
  core/tasks/      # Celery 任务定义
  core/events/     # 事件类型 & 发布
  websocket/       # Consumers / 订阅路由
  auth/            # JWT / 2FA / 权限
  privacy/         # 加密 / 数据留存
  instrumentation/ # 指标 & 链路
  feature_flags/   # Flag 解析
```

## 3. 主调用链示例（Chat → Emotion → Theme）
1. 前端发送消息 → `/api/v1/chat/session/:id/message?stream=true`
2. 后端 ChatService 构造上下文 → 调用 LLMGateway
3. 流式 token 返回 → 每 N tokens 触发 emotion pipeline
4. emotion.updated 通过 WS 推送 → 前端 EmotionContext 更新
5. ThemeEngine 根据 emotion 切换 palette / motion / sound

## 4. 报告生成管线
pending → building (section tasks parallel) → partial ready events → assembling → done

## 5. 私密层隔离
- 入口二次认证 → PST
- 后端中间件校验 X-PST
- Miyu 数据字段级加密 + 分离的 model
- 不写入普通 Chat 语义索引

## 6. 扩展点
| 点 | 如何扩展 |
|----|----------|
| 新报告 Section | 新建 SectionBuilder + 注册 registry |
| 新情感标签 | 扩展 emotion model + 映射 theme map |
| 新学习推荐策略 | 添加策略类并在 RecoEngine 策略选择 |
| 新事件 | 定义 event schema + 发布 + 前端订阅 |

## 7. 决策权衡
| 决策 | 原因 | 替代 |
|------|------|------|
| DRF + Channels | Django 生态与一致性 | FastAPI（需自行集成 ORM 适配） |
| Celery | 成熟、生态广 | Dramatiq/RQ（轻量） |
| ONNX Runtime | 跨平台 + 性能 | PyTorch Serve（更重） |
| WebSocket + SSE 降级 | 实时 + 兼容 | 仅 WS（老浏览器不支持） |

## 8. 下一步
阅读：
- realtime_and_events.md
- ai_pipeline_extension.md