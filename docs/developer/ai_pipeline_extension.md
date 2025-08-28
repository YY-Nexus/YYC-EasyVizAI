# AI 管线扩展指南

## 1. 架构回顾
| 管线 | 位置 | 功能 |
|------|------|------|
| Emotion | core/ai/emotion | 情感分类 + 平滑 |
| Learning Reco | core/ai/learning_path | 路径推荐 |
| Report Build | core/ai/report | Section 生成调度 |
| Code Analyzer | services/code + workers | AST / 图构建 |

## 2. 新增情感标签步骤
1. 微调/选择模型 → ONNX 转换
2. 放置模型文件：`models/emotion_v2.onnx`
3. 扩展 `EmotionModelAdapter` 支持新输出
4. 更新 `EMOTION_MAPPING` (emotion → theme)
5. 加测试：低置信阈值避免 UI 抖动

## 3. 新增学习推荐策略
策略类：
```python
class DifficultyBalancedStrategy(StrategyBase):
    def recommend(self, user_context, graph):
        # 返回 node_id 列表
        return [...]
```
注册：
```python
STRATEGY_REGISTRY["balanced"] = DifficultyBalancedStrategy()
```

## 4. 新增报告 Section 类型
详见 `report_section_plugin.md`

## 5. Prompt 模板管理
- 目录：`core/ai/prompts`
- 模板变量：`{{user_goal}} {{recent_emotions}}`
- 通过 `PromptRenderer` 注入上下文
- 避免：直接拼接用户原文（敏感字段先脱敏）

## 6. 模型版本切换
| 步骤 | 说明 |
|------|------|
| 添加模型配置 | settings.MODEL_CONFIG["emotion"]["v2"] |
| 增加灰度 Flag | feature flag: emotion.model.version=v2 |
| 指标对比 | 推断耗时 / 置信偏差 |
| 切流 | 默认 variant 切至 v2 |

## 7. 推理性能优化
| 技术 | 用途 |
|------|------|
| ONNX Runtime session 重用 | 减少初始化 |
| Batch 聚合 | 汇总多消息文本 |
| 量化 (int8) | 降低延迟 |
| Warmup | 服务启动加载 dummy 请求 |

## 8. 安全与合规
- 禁止 Prompt 泄露内部策略 → 使用 Redaction
- Miyu 原文不进入全局 embedding
- 敏感关键词 → 安全策略降级响应

## 9. 监控指标
| 指标 | 描述 |
|------|------|
| emotion_infer_latency_ms | 情感推断延迟 |
| report_section_fail_total | Section 生成失败次数 |
| code_analysis_avg_time | 平均代码解析时长 |

## 10. 常见扩展错误
| 错误 | 解决 |
|------|------|
| 新 Section 未生效 | 未在 registry 注册 |
| 模型加载慢 | 放在持久存储 / 预热 |
| Emotion 抖动 | smoothing window 太小 |
