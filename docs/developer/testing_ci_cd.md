# 测试 & CI/CD

## 1. 测试金字塔

| 层 | 工具 | 覆盖点 |
|----|------|--------|
| 单元 | pytest / vitest | 纯逻辑 |
| 集成 | pytest (API) | DB / 服务交互 |
| E2E | Playwright/Cypress | 用户旅程 |
| 负载 | k6 / Locust | 性能 |
| 安全 | ZAP | OWASP Top10 |
| 合约 | schemathesis | OpenAPI 约束 |

## 2. 覆盖指标

| 模块 | 目标 |
|------|------|
| services/* | ≥80% |
| core/ai | ≥70% |
| websocket | 基础路径覆盖 |
| frontend components | 行覆盖 60%+ (关键组件 80%) |

## 3. CI 流程（GitHub Actions 建议）

1. checkout + 缓存
2. 后端：lint → type → test
3. 前端：lint → type → test
4. OpenAPI 生成 → spectral 校验
5. 构建 Docker 镜像（带标签）
6. k8s staging 部署（可选）
7. Smoke Test

## 4. 常用命令

| 指令 | 说明 |
|------|------|
| make test-backend | 仅后端 |
| make test-frontend | 仅前端 |
| make contract | OpenAPI 合约回归 |
| make e2e | E2E 测试（需 env 启动） |

## 5. 合约测试（schemathesis）

```bash
schemathesis run http://localhost:8000/openapi/v1.yaml --checks all
```

## 6. 回归套件

- Chat 基础
- Miyu 进入 + 日记 CRUD
- 报告 task 分段
- Code 小规模文件
- 图谱节点完成
- Emotion 推送

## 7. 发布策略

| 环境 | 分支 | 验证 |
|------|------|------|
| dev | 任意 feature PR | 自动构建 |
| staging | main 合并 | E2E + 性能冒烟 |
| prod | tag vX.Y.Z | 人工批准 + 蓝绿 / 灰度 |

## 8. 回滚

- 通过上一个稳定 tag
- 数据迁移：使用 reversible migrations
- Feature Flag 快速关闭新功能
