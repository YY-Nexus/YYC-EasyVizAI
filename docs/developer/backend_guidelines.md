# 后端开发规范

## 1. 代码风格

| 工具 | 规则 |
|------|------|
| ruff | lint |
| black | 格式化 |
| isort | 导入排序 |
| mypy | 类型检查 |

执行：

```bash

make lint
make type
```

## 2. 模块边界

- api 层：只做序列化 / 鉴权 / 调用 service
- service：业务组合 + 事务控制
- model：纯数据结构，不写复杂业务
- core/ai：模型推理与预处理
- core/tasks：异步任务定义（避免直接写在 service）
- instrumentation：统一 metrics/tracing 封装

## 3. Service 模板（示例）

```python
class ReportService:
    def __init__(self, repo: ReportRepository, publisher: EventPublisher):
        self.repo = repo
        self.publisher = publisher

    def create_task(self, user, payload):
        task = self.repo.create(user, payload)
        publish_event("report.task.created", task_id=task.id)
        return task
```

## 4. 事务与幂等

- 使用 `select_for_update` 锁定需要串行更新的行
- 对外部写操作支持 Idempotency-Key 头（在视图层解析）

## 5. 加密

- 私密字段：调用 `encrypt_field(data, key_ref)`
- 加密列以 `_enc` 结尾
- 不在日志输出加密前明文

## 6. 日志

结构化：

```python
logger.info(
  "report_section_ready",
  extra={"task_id": t.id, "section": sid, "trace_id": get_trace_id()}
)
```

## 7. 指标（Prometheus 示例）

```python
report_section_latency = Histogram(
  "report_section_latency_seconds", "Section build duration", ["section_type"]
)
```

## 8. 事件发布

```python
from app.core.events import publish_event
publish_event("report.section.ready", data={"task_id": t.id, "section_id": sid})
```

## 9. Celery 队列

| 队列 | 用途 |
|------|------|
| default | 通用轻任务 |
| report | 报告段生成 |
| code | 代码解析 |
| emotion | 批量情感分析 |

启动：

```bash
celery -A app.core.tasks worker -Q report -c 2
```

## 10. API 变更流程

1. 新增字段：补 tests + OpenAPI + 前端适配
2. 废弃字段：标记 deprecate 字段 + 发布 changelog
3. 破坏变更：发起 RFC issue + 版本 bump

## 11. 性能建议

- N+1：select_related / prefetch_related
- 缓存：短期（Redis）+ 结果 hash（代码图）
- 批量推理：emotion pipeline 允许 batch 请求

## 12. 安全

- 所有访问私密层的 API 验证 X-PST
- request.user.id 记录 trace 但不写入 Miyu 原文

## 13. 单元测试风格

```python
def test_report_task_creation(report_service, user):
    task = report_service.create_task(user, {"sections":[]})
    assert task.id
```

## 14. 目录约束

- 不在 api/ 下写业务
- 不在 services/ 内直接 import views
- 不交叉引用 service（用 facade 聚合）

## 15. 常见反模式

| 反模式 | 替代 |
|--------|------|
| 在 view 中写复杂事务 | service 中封装 |
| 直接调用模型保存加密字段 | 使用 encryption util |
| 发布事件结构不统一 | 使用统一 event publisher |
| 大文件同步处理 | 异步任务化 |
