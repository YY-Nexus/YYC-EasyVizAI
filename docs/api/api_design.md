# YYC³ EasyVizAI API 设计文档 (v1 Draft)

> 本文档定义 YYC³ EasyVizAI 平台后端 HTTP / WebSocket / 事件总线 API 设计规范与主要接口，用于前后端协同、测试、合规与可扩展规划。  
> 覆盖：命名规范、版本策略、鉴权、错误码、速率限制、模块端点、数据模型、流式协议、示例、未来扩展钩子。  
> 对应系统架构与功能模块文档（core_architecture.md / function_modules_design.md）。

---

## 1. 版本 / 基础约定

| 项 | 约定 |
|----|------|
| Base URL | https://api.easyvizai.com |
| Versioning | 前缀路径法：/api/v1/...；重大破坏性变更 → 新版本 /v2 保留 v1 ≥12 个月 |
| Content-Type | application/json; charset=utf-8（流式 SSE: text/event-stream；上传 multipart/form-data） |
| Encoding | UTF-8 |
| Time | ISO8601 UTC（2025-08-27T10:15:30Z） |
| ID | 短前缀 + ULID/UUID（如 rpt_01HF....、task_...、msg_...） |
| Pagination | Cursor 优先：?limit=20&cursor=xxxx；回传 next_cursor |
| Sorting | ?sort=field(-desc 默认 asc) |
| Filtering | 统一字段匹配 ?status=done&from=...&to=... |
| Null vs Omit | 无值字段省略，不返回 null（节省带宽） |

---

## 2. 鉴权与安全

| 场景 | 机制 |
|------|------|
| 标准访问 | Bearer JWT Access Token（15~30m）+ Refresh Token |
| 私密层 (Miyu) | 进入后需二次认证 (TOTP / WebAuthn Assertion) → 颁发短期 PrivateSpace Token (PST, 30m) |
| 内部服务 | mTLS / HMAC 签名头 X-YYC-Signature |
| 重放防护 | nonce + 5 分钟时效（内部签名接口） |
| 权限模型 | RBAC + Feature Flag + ABAC(私密层 + 设备指纹) |
| Scope (可选) | access_token 中加入 scopes: ["chat:write","miyu:read"] |
| 加密字段 | 后端 envelope encryption；Miyu 内容可选前端预加密 |

示例请求头：
```
Authorization: Bearer eyJhbGciOi...
X-PST: pst_xxx   # 仅私密层接口需要
```

---

## 3. 错误与响应格式

统一响应：
```
# 成功
{
  "data": {...},
  "meta": { "trace_id": "trc_01HF...", "t": "2025-08-27T22:30:01Z" }
}

# 失败
{
  "error": {
    "code": "INVALID_PARAM",
    "message": "node_id missing",
    "details": { "field": "node_id" },
    "trace_id": "trc_01HF..."
  }
}
```

常见错误码：

| Code | HTTP | 说明 |
|------|------|------|
| UNAUTHENTICATED | 401 | 缺少或失效 Token |
| UNAUTHORIZED | 403 | 权限不足 / Flag 关闭 |
| INVALID_PARAM | 400 | 参数/格式错误 |
| VALIDATION_FAILED | 422 | 语义校验失败 |
| NOT_FOUND | 404 | 资源不存在 |
| RATE_LIMITED | 429 | 频次超限 |
| CONFLICT | 409 | 状态冲突（重复提交 / 并发） |
| TASK_NOT_READY | 425 | 异步结果尚未就绪 |
| INTERNAL_ERROR | 500 | 未捕获异常 |
| SERVICE_UNAVAILABLE | 503 | 下游不可用 |
| ENCRYPTION_ERROR | 500 | 加密/解密失败 |
| MIYU_2FA_REQUIRED | 403 | 需二次认证 |
| MIYU_ACCESS_REVOKED | 403 | 私密层禁用 |
| FEATURE_FLAG_DISABLED | 403 | 功能未开放 |
| QUOTA_EXCEEDED | 402 | 配额耗尽（未来付费） |

---

## 4. 速率限制 (Rate Limiting)

| 端点类别 | 基准额度 (User) | 备注 |
|----------|----------------|------|
| Chat 发送 | 60 req / 分钟 / user | 按 session_id 限频子窗口 |
| Emotion 分析 (内部) | 200 / 分钟 / 服务 | 批处理 |
| 报告 task 创建 | 5 / 分钟 / user | 超过返回 QUOTA_EXCEEDED |
| 代码分析 | 10 / 小时 / user | 后续可按行数加权 |
| Miyu 日记 | 30 / 小时 / user | 限制滥用 |
| WebSocket 连接 | 3 并发 / user | 超出断开最旧连接 |

响应头（限频命中时返回）：
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 3
X-RateLimit-Reset: 1724791830
```

---

## 5. 模块端点详列

### 5.1 Auth & 用户

| Method | Path | 描述 |
|--------|------|------|
| POST | /api/v1/auth/login | 用户登录（帐号+密码/第三方） |
| POST | /api/v1/auth/refresh | 刷新 Token |
| POST | /api/v1/auth/logout | 注销 |
| GET  | /api/v1/auth/me | 当前用户信息 |
| POST | /api/v1/auth/mfa/totp/verify | TOTP 验证 |
| POST | /api/v1/auth/mfa/webauthn/assert | WebAuthn 断言 |
| GET  | /api/v1/auth/flags | 返回用户 Feature Flags |

示例：登录
```
POST /api/v1/auth/login
{ "username":"user1", "password":"***" }

200
{
  "data": {
    "access_token":"...",
    "refresh_token":"...",
    "expires_in":1800,
    "miyu_enabled": true
  }, "meta": {...}
}
```

### 5.2 Chat 会话

| Method | Path | 功能 |
|--------|------|------|
| POST | /api/v1/chat/session | 创建会话 |
| GET  | /api/v1/chat/session/{id} | 获取元信息 |
| POST | /api/v1/chat/session/{id}/message?stream=true | 发送消息（可流式） |
| GET  | /api/v1/chat/session/{id}/history?cursor=... | 历史分页 |
| POST | /api/v1/chat/session/{id}/regenerate/{msg_id} | 重生回答 |
| DELETE | /api/v1/chat/session/{id} | 归档或删除会话 |
| POST | /api/v1/chat/session/{id}/tool-call | 工具触发（学习/代码/报告） |

发送流式（SSE）：
```
POST /api/v1/chat/session/sess_123/message?stream=true
Accept: text/event-stream

data: {"event":"chunk","content":"Hello"}
data: {"event":"chunk","content":" world"}
data: {"event":"emotion","emotion":"calm","confidence":0.82}
data: {"event":"done","message_id":"msg_456"}
```

### 5.3 Emotion (内部/私有)

| Method | Path | 说明 |
|--------|------|------|
| POST | /internal/emotion/analyze | 批量分析（内部调用） |
| GET  | /api/v1/emotion/recent?limit=50 | （用户）最近情绪日志（脱敏） |
| WS   | channel: emotion.updated | 推送最新稳定情绪标签 |

请求：
```
POST /internal/emotion/analyze
{ "items":[ {"id":"msg_1","text":"..."} ], "lang":"zh" }
```

响应：
```
{ "data":[ {"id":"msg_1","emotion":"stressed","confidence":0.87} ] }
```

### 5.4 Miyu 私密层

| Method | Path | 描述 |
|--------|------|------|
| POST | /api/v1/miyu/auth/enter | 发起进入（返回需二次验证类型） |
| POST | /api/v1/miyu/auth/verify | 校验 2FA → 返回 PST Token |
| GET  | /api/v1/miyu/diary?cursor=... | 列出日记（解密后传输 or 客户端解密） |
| POST | /api/v1/miyu/diary | 创建日记 |
| GET  | /api/v1/miyu/diary/{id} | 获取单条 |
| DELETE | /api/v1/miyu/diary/{id} | 软删除（日记） |
| POST | /api/v1/miyu/diary/{id}/destroy | 即时硬删除 |
| POST | /api/v1/miyu/config/retention | 设置留存策略 |
| POST | /api/v1/miyu/relax/breath | 启动呼吸引导 session |
| GET  | /api/v1/miyu/relax/breath/{session_id}/status | 状态查询 |

日记创建：
```
POST /api/v1/miyu/diary
X-PST: pst_abc
{
  "cipher_blob": "Base64(EncryptedPayload)",
  "emotion_hint": "stressed",
  "client_encryption": true
}
```

响应：
```
201
{ "data": { "entry_id":"myd_01HF...", "created_at":"..." } }
```

### 5.5 Learning Path

| Method | Path | 描述 |
|--------|------|------|
| GET  | /api/v1/learning/graph | 返回图谱（可分块） |
| GET  | /api/v1/learning/progress | 当前进度 |
| POST | /api/v1/learning/node/{node_id}/complete | 标记完成 |
| GET  | /api/v1/learning/recommendations | 推荐新节点 |
| GET  | /api/v1/learning/diff?since=timestamp | 自上次的图差异 |

Graph 样例：
```
{
 "data": {
   "nodes":[{"id":"n_intro","label":"基础","prereq":[],"difficulty":1}],
   "edges":[{"from":"n_intro","to":"n_advanced"}]
 }
}
```

### 5.6 Code Intelligence

| Method | Path | 描述 |
|--------|------|------|
| POST | /api/v1/code/analyze?async=true | 提交代码分析任务 |
| GET  | /api/v1/code/task/{id}/status | 状态 |
| GET  | /api/v1/code/task/{id}/graph | 图数据（完成后） |
| GET  | /api/v1/code/task/{id}/stages | 阶段明细（百分比） |
| DELETE | /api/v1/code/task/{id} | 取消/删除缓存 |

提交：
```
POST /api/v1/code/analyze?async=true
Content-Type: multipart/form-data
files[]: (source.py)
options: {"language":"python","explain":true}
```

Status:
```
{
 "data":{
   "task_id":"code_01HF...",
   "state":"graph_layout",
   "progress":0.55,
   "stages":[
     {"name":"scanning","done":true},
     {"name":"ast_build","done":true},
     {"name":"graph_layout","percent":55}
   ]
 }
}
```

### 5.7 Report Builder

| Method | Path | 描述 |
|--------|------|------|
| POST | /api/v1/report/task | 创建报告任务 |
| GET  | /api/v1/report/task/{id}/status | 状态 |
| GET  | /api/v1/report/task/{id}/sections | 列出已就绪 Section |
| GET  | /api/v1/report/task/{id}/section/{sid} | 单段内容 |
| GET  | /api/v1/report/task/{id}/artifact?format=pdf | 总产物 |
| DELETE | /api/v1/report/task/{id} | 取消任务 |

创建：
```
POST /api/v1/report/task
{
 "title":"学习周报",
 "sections":[
   {"id":"intro","type":"summary","prompt":"总结本周进展"},
   {"id":"graph","type":"learning_graph_snapshot"},
   {"id":"emotion","type":"emotion_curve","range_days":7}
 ]
}
```

Status:
```
{
 "data":{
   "task_id":"rpt_01HF...",
   "state":"section_partial",
   "completed_sections":2,
   "total_sections":5,
   "progress":0.4
 }
}
```

### 5.8 Feature Flags

| Method | Path | 描述 |
|--------|------|------|
| GET | /api/v1/flags | 用户评估后的 flags (variant) |
| POST | /api/v1/admin/flags | 创建/更新（管理员） |
| GET | /api/v1/admin/flags/audit | 操作日志 |

### 5.9 资产/文件

| Method | Path | 描述 |
|--------|------|------|
| POST | /api/v1/assets/upload | 上传（通用） |
| GET  | /api/v1/assets/{id} | 获取（鉴权临时URL） |
| DELETE | /api/v1/assets/{id} | 删除 |

### 5.10 Admin / 审计

| Method | Path | 描述 |
|--------|------|------|
| GET | /api/v1/admin/users?cursor= | 用户列表 |
| GET | /api/v1/admin/user/{id} | 用户详情（无 Miyu 明文） |
| GET | /api/v1/admin/audit?type=... | 审计事件 |
| GET | /api/v1/admin/metrics | 平台指标（权限控制） |

---

## 6. WebSocket 协议

连接：
```
wss://api.easyvizai.com/ws?access_token=...&topics=chat:sess_123,report:rpt_456,emotion:user
```

初始 Server → Client:
```
{
 "type":"welcome",
 "connection_id":"ws_01HF...",
 "heartbeat_interval":30000
}
```

心跳：
```
Client → {"type":"ping","t":173...}
Server → {"type":"pong","t":173...}
```

统一事件消息：
```
{
 "type":"event",
 "channel":"report.section.ready",
 "ts":1735345,
 "payload":{
   "task_id":"rpt_01HF",
   "section_id":"intro",
   "url":"https://.../intro.json"
 }
}
```

增量聊天 token：
```
{
 "type":"stream",
 "channel":"chat.message.stream",
 "payload":{
   "session_id":"sess_123",
   "message_id":"msg_456",
   "delta":"下一段"
 }
}
```

Emotion：
```
{
 "type":"event",
 "channel":"emotion.updated",
 "payload":{"emotion":"stressed","confidence":0.81}
}
```

---

## 7. 事件主题 (Event Bus) Schema 摘要

| Topic | Schema 关键字段 |
|-------|----------------|
| chat.message.stream | session_id, message_id, seq, delta |
| emotion.updated | user_id, emotion, confidence |
| learning.node.completed | user_id, node_id |
| learning.path.recommended | user_id, diff[] |
| code.analysis.stage_progress | task_id, stage, percent |
| code.analysis.completed | task_id, success, graph_ref |
| report.section.ready | task_id, section_id, artifact_ref |
| report.task.progress | task_id, state, progress |
| miyu.entry.created | user_id(hash), entry_id, ts |
| security.miyu.access | user_id, result, reason |
| feature.flag.evaluated | user_id, flag_id, variant |

公共事件 envelop：
```
{
 "id":"evt_01HF...",
 "type":"report.section.ready",
 "ts":1735345,
 "actor":"user:123",
 "data":{...},
 "trace_id":"trc_..."
}
```

---

## 8. 数据模型 (API 层结构体示例)

ChatMessage (响应)：
```
{
 "message_id":"msg_...",
 "role":"assistant",
 "content":"文本",
 "tokens":123,
 "created_at":"2025-08-27T...",
 "emotion_snapshot":"calm"
}
```

ReportSection：
```
{
 "section_id":"intro",
 "type":"summary",
 "state":"ready",
 "content":{
   "text":"......",
   "media":[{"type":"chart","url":"..."}]
 },
 "updated_at":"..."
}
```

MiyuDiary（解密后）：
```
{
 "entry_id":"myd_...",
 "content":"（明文或已在前端解密）",
 "emotion_hint":"stressed",
 "created_at":"...",
 "retention_policy":"30d"
}
```

---

## 9. 任务状态机（API 可见字段）

| 任务 | 状态字段 | 终态 |
|------|----------|------|
| 报告 | pending → building → section_partial(循环) → assembling → done / failed | done / failed |
| 代码 | queued → scanning → ast_build → graph_layout → enriching → done / failed | done / failed |
| 学习推荐 | scheduled → computing → done | done |
| Miyu 呼吸 | initializing → running → finished / canceled | finished / canceled |

统一任务状态查询返回：
```
{
 "data":{
   "task_id":"code_01HF...",
   "type":"code_analysis",
   "state":"ast_build",
   "progress":0.34,
   "started_at":"...",
   "updated_at":"...",
   "eta_seconds":12
 }
}
```

---

## 10. Streaming & 差分策略

| 场景 | 机制 | Payload 模式 |
|------|------|--------------|
| Chat | SSE / WS | 增量 token |
| 报告 | WS | Section Ready 事件 + pull 内容 |
| 学习图 | WS | diff: {added_nodes, unlocked_nodes} |
| 代码图 | WS | stage_progress → 局部子图抓取 |
| Emotion | WS | 固定最小间隔 1.5s / 阈值变化 |
| Miyu 呼吸 | WS (可选) | step: inhale/exhale/hold |

Graph diff 样例：
```
{
 "type":"event",
 "channel":"learning.path.recommended",
 "payload":{
   "diff":{
     "added_nodes":[{"id":"n_algo2","prereq":["n_algo1"]}],
     "unlocked":["n_ds_basic"]
   }
 }
}
```

---

## 11. 查询与过滤示例

分页：
```
GET /api/v1/chat/session/sess_123/history?limit=30&cursor=msg_01HF...

{
 "data":[...],
 "meta":{"next_cursor":"msg_01HG...", "has_more":true}
}
```

学习节点过滤（未来）：
```
GET /api/v1/learning/graph?tag=python&difficulty<=3
```

---

## 12. 安全 / 合规附加 Header

| Header | 用途 |
|--------|------|
| X-Client-Version | 前端版本（灰度/诊断） |
| X-Device-Id | 设备指纹散列（ABAC） |
| X-Request-Id | 幂等性 / Trace 透传 |
| X-PST | 私密层访问 Token |
| X-Data-Redaction | "on" 时服务端不回传部分原文（审计模式） |

幂等性（对可重试写操作）：
```
POST /api/v1/report/task
Idempotency-Key: 01HFG7...

返回若重复：HTTP 201 + 标记 "idempotent":true
```

---

## 13. Feature Flag 评估方式

请求：
```
GET /api/v1/flags
```

响应：
```
{
 "data":[
   {"flag_id":"miyu.layer.enabled","variant":"on"},
   {"flag_id":"emotion.theme.mapping","variant":"gentle"}
 ],
 "meta":{"version":"ff_2025-08-27T22:30Z"}
}
```

---

## 14. 速率/配额查询（未来）

```
GET /api/v1/usage
{
 "data":{
   "chat_messages":{"used":340,"limit":500},
   "report_tasks":{"used":2,"limit":10},
   "code_analysis":{"used":5,"limit":10}
 }
}
```

---

## 15. 开发 / 测试工具端点 (仅非生产)

| Method | Path | 用途 |
|--------|------|------|
| POST | /dev/mock/emotion | 注入假情绪 |
| POST | /dev/reset/user/{id} | 重置用户数据 |
| GET  | /dev/health/full | 依赖健康报告 |

---

## 16. 版本迁移策略

- v1 → v2：  
  - 新功能添加字段 => 向后兼容  
  - 字段弃用：标记 `x-deprecated: true`，文档说明 + 90 天观察  
  - 破坏性更改：提供 /api/v2/... 新端点并并行运营  
- OpenAPI 文档：`/openapi/v1.yaml`，每日构建校验（diff 报警）  

---

## 17. OpenAPI 元数据（摘要）

| Info | 内容 |
|------|------|
| title | YYC³ EasyVizAI API |
| version | 1.0.0-draft |
| servers | https://api.easyvizai.com / https://sandbox.api.easyvizai.com |
| securitySchemes | bearerAuth, pstAuth, hmacSig |
| tags | Auth, Chat, Emotion, Miyu, Learning, Code, Report, Flags, Admin |

---

## 18. 性能与 SLA 显示端点（Admin）

```
GET /api/v1/admin/metrics
{
 "data":{
   "latency":{"chat_p95_ms":140,"report_section_p95_ms":3200},
   "queue":{"report_depth":3,"code_depth":0},
   "ws":{"active_connections":512},
   "emotion":{"infer_p95_ms":68}
 }
}
```

---

## 19. 安全与审计事件示例

```
GET /api/v1/admin/audit?type=security.miyu.access&from=...
{
 "data":[
   {
     "event_id":"evt_...",
     "type":"security.miyu.access",
     "user_id":"u_123",
     "result":"success",
     "ip":"203.0.113.8",
     "ts":"2025-08-27T22:01:11Z"
   }
 ]
}
```

---

## 20. 未来扩展占位

| 模块 | 预留端点 |
|------|----------|
| 多智能体 | /api/v1/agents/session, /api/v1/agents/cooperate |
| 企业多租户 | /api/v1/orgs, /api/v1/orgs/{id}/members |
| Billing | /api/v1/billing/subscribe, /api/v1/billing/invoices |
| 记忆与私人语义 | /api/v1/memory/chunk, /api/v1/memory/search |

---

## 21. 安全最佳实践摘要

| 场景 | 设计 |
|------|------|
| Chat Prompt 注入 | 服务端清洗 + 上下文截断 |
| 私密数据备份 | 加密后冷备；KeyRef 不入备份 |
| Token 洩漏 | 旋转机制 + Refresh 黑名单 |
| 事件重放 | 每事件 ID 幂等处理 |
| 反爬 | 动态节流 + 风险分数 |

---

## 22. 附录：示例 JSON Schema 片段

ChatMessageSchema（简化）：
```
{
 "$id":"https://api.easyvizai.com/schema/chat_message.json",
 "type":"object",
 "properties":{
   "message_id":{"type":"string","pattern":"^msg_"},
   "role":{"type":"string","enum":["user","assistant","system","tool"]},
   "content":{"type":"string"},
   "tokens":{"type":"integer","minimum":0},
   "created_at":{"type":"string","format":"date-time"},
   "emotion_snapshot":{"type":"string"}
 },
 "required":["message_id","role","content","created_at"]
}
```

---

## 23. 质量与发布控制

| 检查 | 工具 |
|------|------|
| OpenAPI 静态校验 | spectral |
| 合约回归 | schemathesis |
| 性能基准 | k6 脚本 / GitLab CI Stage |
| 安全扫描 | ZAP（动态）、Bandit/Trivy（静态） |
| 事件 Schema 验证 | Avro / JSON Schema Registry |

---

## 24. 实施优先级 (P0-P2)

| 级别 | 模块 | 端点 |
|------|------|------|
| P0 | Auth / Chat / Emotion (core) | 登录 / 会话 / 流式 / emotion.updated |
| P0 | Miyu 基础 | enter / verify / diary CRUD |
| P1 | Learning / Report / Code | graph / report task / code analyze |
| P1 | Realtime WS 聚合 | 统一 topics 订阅 |
| P2 | Feature Flags / Admin | flags / metrics / audit |
| P2 | Retention / Destroy | Miyu retention & destroy |

---

## 25. 变更控制

| 变更类型 | 处理 |
|----------|------|
| 新字段 | 文档更新 + 增量兼容 |
| 字段弃用 | 标记 deprecated + 90 天后移除 |
| 错误码新增 | 文档增补 + 客户端回退策略 |
| Endpoint 废弃 | /deprecated 一段时间重定向提示 |
| 流式事件结构变更 | 新增 event_version 字段 |

---

## 26. 总结

该 API 设计围绕：可扩展事件流、私密隔离、安全合规、实时体验与多模态生成。按优先级迭代可快速形成首个闭环并支持未来多智能体、企业化与商业模式拓展。

> 下一步建议：生成 openapi_v1.yaml 初稿；针对 Chat、Report、Miyu 端点编写 Schemathesis 测试计划；接入 spectral 校验 CI。
