# 安全与隐私规范

## 1. 数据分级

| 等级 | 数据 | 示例 | 存储 |
|------|------|------|------|
| 低 | 公共结构 | 学习节点 | RDB |
| 中 | 会话内容 | 普通 Chat | RDB / Vector |
| 高 | 私密日记 | MiyuEntry | 加密 RDB |
| 最高 | 加密密钥 | KeyRef / KMS | Vault |

## 2. 加密策略

| 项 | 方法 |
|----|------|
| 字段加密 | AES-GCM envelope (key_ref) |
| 对象存储 | 服务端加密 + KeyRef 元数据 |
| 客户端加密 | Miyu 可选（cipher_blob） |

## 3. 密钥管理

- Vault / KMS 生成 master key
- 应用侧只持有 data key (缓存短期)
- rotate_keys.sh 每季度换密钥 + rewrap

## 4. 访问控制

| 层 | 控制 |
|----|------|
| API | JWT / PST |
| GraphQL(未来) | Scope + Field Resolver |
| WebSocket | 连接鉴权 + topic 白名单 |

## 5. Miyu 隐私

- 不写日志、不做 embedding
- EmotionLog 不存原文，只存标签 + hash 摘要
- Retention 定时清理 + 软删除→硬删除

## 6. 输入清洗

- Prompt 注入：转义控制符 / 限制系统指令注入
- 代码上传：黑名单文件类型（.exe, .dll）

## 7. 防滥用

| 威胁 | 措施 |
|------|------|
| 高频接口刷写 | IP/User 限频 + Redis 计数 |
| 任务轰炸 | Queue length 超阈限流 |
| 代码解析 CPU 爆炸 | 文件大小/行数限制 |
| 词法注入 | 禁用内嵌执行 eval 类操作 |

## 8. 日志与脱敏

- 清洗字段：password, cipher_blob, tokens
- 使用 JSON Logger + trace_id

## 9. 审计

事件类型：

- security.miyu.access
- feature.flag.evaluated
- data.retention.cleanup
- admin.action.*

## 10. 数据销毁

- Miyu 删除 → 软标记 deleted_at
- 48h grace period → 任务硬删除（不在 UI 暴露恢复）
- Vector 索引中相关 embedding 立即删除

## 11. 安全测试

| 类型 | 工具 |
|------|------|
| SAST | Bandit |
| 依赖漏洞 | pip-audit / npm audit / Trivy |
| DAST | OWASP ZAP |
| 审计 | 自定义 SQL 查询 |

## 12. 响应流程

| 等级 | 说明 | 行动 |
|------|------|------|
| P0 | 私密数据泄露 | 封禁通道，Key rotate |
| P1 | 身份伪造 | 日志追踪，风控增强 |
| P2 | 资源滥用 | 限流+黑名单 |
