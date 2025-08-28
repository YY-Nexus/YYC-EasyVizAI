# 报告 Section 插件开发

## 1. 目标

动态扩展报告组成部分（Section），支持多类型：summary / emotion_curve / learning_snapshot / custom_chart。

## 2. 接口

```python
class BaseSectionBuilder:
    section_type = "abstract"
    def validate(self, payload): ...
    def build(self, context) -> SectionResult: ...
```

## 3. 注册

```python
from .registry import register
@register("emotion_curve")
class EmotionCurveSection(BaseSectionBuilder):
    ...
```

## 4. 构造上下文

- 用户最近 N 天 EmotionLog 聚合
- 学习进度摘要
- Chat 主题关键词（脱敏）

## 5. 并行执行

- Celery 并发
- Section 失败：标记 error + 可重试

## 6. 输出格式

```json
{
 "section_id":"emotion",
 "type":"emotion_curve",
 "content":{
   "chart":{
     "points":[{"t":"2025-08-26","calm":0.4,"stressed":0.2}]
   },
   "summary":"过去7天整体情绪平稳..."
 }
}
```

## 7. 常见问题

| 问题 | 解决 |
|------|------|
| Section 缺失 | 未注册 / 名称冲突 |
| 生成超时 | 拆分子步骤 / 提前聚合数据 |
| 泄露私密 | Miyu 原文不可参与上下文 |
