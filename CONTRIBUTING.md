# 贡献指南

## 1. 交流渠道
- Issues：缺陷/改进
- Discussions：架构 / 设计建议
- PR：功能实现或修复

## 2. 工作流
1. 创建 Issue 获取共识
2. fork / 新建分支
3. 提交规范：
```
feat(report): add emotion curve section
fix(miyu): correct PST expiry bug
```
4. 发起 PR → 自动 CI → 代码评审 → 合并

## 3. 评审原则
| 项 | 标准 |
|----|------|
| 可读性 | 清晰函数命名 |
| 模块边界 | API/Service/Model 不混用 |
| 安全 | 无敏感数据输出 |
| 性能 | 无明显低效循环/查询 |
| 测试 | 正常 + 边界覆盖 |

## 4. 分支命名
| 类型 | 格式 |
|------|------|
| 功能 | feature/<scope>-<desc> |
| 修复 | fix/<issue|desc> |
| 热修 | hotfix/<desc> |
| 实验 | experiment/<desc> |

## 5. 发布标签
语义化版本：MAJOR.MINOR.PATCH
- 破坏性：+1 MAJOR
- 新功能：+1 MINOR
- 修复：+1 PATCH

## 6. Code Owners（示范，可在 CODEOWNERS 配置）
```
/backend/app/services/report @team-report
/frontend/src/modules/miyu @team-experience
```

## 7. 许可与版权
- 贡献即视为同意项目 LICENSE（待确定）
- 如引入第三方代码需注明来源与授权

## 8. 开放事项
| 主题 | 需要贡献 |
|------|----------|
| 新报告 Section | 数据可视化/图表 |
| Emotion 模型优化 | 低延迟策略 |
| Code Parser 适配 | 更多语言 |
| A11y 优化 | 高对比/键盘导航 |

感谢你的贡献！