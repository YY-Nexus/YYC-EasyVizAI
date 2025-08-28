# 数据模型参考（摘要）

## 1. 用户 & 权限

- User(id, role, flags_cache)
- FeatureFlagEval(user_id, flag_id, variant)

## 2. Chat

- ChatSession(id, user_id, title, created_at)
- ChatMessage(id, session_id, role, content, tokens, emotion_snapshot, created_at)

## 3. Miyu 私密

- PrivateSpace(user_id, key_ref)
- MiyuEntry(id, ps_id, cipher_blob, retention, created_at, deleted_at?)
- EmotionLog(id, user_id, emotion, confidence, ts, context_hash)

## 4. 学习路径

- LearningNode(id, prerequisites[], difficulty)
- LearningProgress(user_id, node_id, status, last_updated)

## 5. 报告

- ReportTask(id, user_id, state, progress, created_at)
- ReportSection(id, task_id, type, state, content_ref)
- ReportArtifact(id, task_id, url, created_at)

## 6. 代码解析

- CodeTask(id, user_id, state, hash, lang)
- CodeArtifact(id, task_id, stage, graph_json_ref)

## 7. 审计

- AuditEvent(id, type, actor_id, ts, meta_json)

## 8. Retention 配置

- RetentionPolicy(id, user_id, type, duration)

## 9. 索引/向量

- SemanticIndex(doc_id, embedding, meta)

## 10. 加密说明

- key_ref 指向 KMS 外部主密钥
- MiyuEntry 不建全文索引
