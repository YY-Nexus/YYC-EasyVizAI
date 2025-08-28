# YYC³ EasyVizAI 开发者文档索引

欢迎加入 YYC³ EasyVizAI 项目。本索引指引你快速找到研发所需内容。

## 快速导航
| 主题 | 文档 |
|------|------|
| 本地环境搭建 | getting_started.md |
| 架构导览 | architecture_walkthrough.md |
| 后端开发规范 | backend_guidelines.md |
| 前端开发规范 | frontend_guidelines.md |
| 实时/事件/流式 | realtime_and_events.md |
| AI 管线扩展 | ai_pipeline_extension.md |
| 报告 Section 插件 | report_section_plugin.md |
| 代码智能解析流程 | code_intelligence_pipeline.md |
| 安全 & 隐私 | security_privacy.md |
| 可观测 & 性能 | observability_performance.md |
| 测试 & CI/CD | testing_ci_cd.md |
| 特性开关/实验 | feature_flags.md |
| 设计 Token & 体验 | design_tokens_and_experience.md |
| 数据模型参考 | data_models_reference.md |
| 贡献指南 | /CONTRIBUTING.md |
| 检查清单 | checklists.md |

## 角色阅读建议
- 新人：getting_started → architecture_walkthrough → backend/frontend_guidelines
- AI 扩展：ai_pipeline_extension + report_section_plugin + code_intelligence_pipeline
- 安全/合规：security_privacy + data_models_reference
- 运维/平台：observability_performance + testing_ci_cd + feature_flags

## 关键约定
- 语言：后端 Python (Django + DRF + Channels / Celery)，前端 React + TS + Vite
- 主干分支：main （受保护）
- 分支命名：feature/<scope>-<short_desc>, fix/<issue>, hotfix/<critical>
- 提交格式：Conventional Commits (feat:, fix:, docs:, refactor:, chore:, test:, perf:, ci:, build:)

更新本索引请保持表格顺序与文件命名一致。