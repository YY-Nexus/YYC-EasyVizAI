# 前端开发规范

## 1. 技术栈
React + TypeScript + Vite + Zustand/Redux（store）+ Framer Motion + Lottie + Howler + OpenFeature (flags)

## 2. 结构回顾
```
src/
  modules/
  design-system/
  context/
  hooks/
  services/{api,ws}
  assets/{lottie,svg,sounds}
  store/slices
  types/
```

## 3. 代码风格
| 工具 | 配置 |
|------|------|
| ESLint | airbnb + 自定义 |
| Prettier | 格式化 |
| Stylelint | 样式 |
| tsc --noEmit | 类型检查 |

## 4. 组件分层
| 层 | 说明 |
|----|------|
| primitives | Button, Card, Modal |
| composite | ChatPanel, ReportPreview |
| feature module | MiyuDiary, CodeGraph |
| pages | 路由入口 |

## 5. 状态管理
| 类型 | 存放 |
|------|------|
| UI 短期状态 | 内部 useState |
| 跨模块 UI | context (EmotionContext) |
| 业务数据缓存 | store slice |
| 实时数据 | RealtimeComposer + local cache |

## 6. API 调用
- 统一封装：`src/services/api/http.ts`
- 自动附加 Token / PST
- 错误处理 → toast / 降级

## 7. 流式消费（SSE）
```ts
const es = new EventSource(url);
es.onmessage = (e) => { /* parse chunk */ };
```

## 8. WebSocket Hook
见 `useRealtimeComposer.ts` 示例（后附）。

## 9. Emotion → Theme
```ts
const { state } = useEmotion();
const theme = mapEmotionToTheme(state.emotion);
```

## 10. 设计 Tokens
构建脚本生成：
- tokens.json → css variables (`:root { --color-ink: #1A3E5E; }`)
- TypeScript 常量 → 智能提示

## 11. 动画原则
| 场景 | 时长 | 缓动 |
|------|------|------|
| route 过渡 | 240ms | standard |
| 节点解锁 | 400ms | emphasize |
| 情感切换 | 600ms 淡入 | standard |

## 12. 声效加载
- Lazy：首次需要时 import()
- 用户“减少动效”→ 禁用声效

## 13. Feature Flag
```ts
const flagClient = useOpenFeature();
const enabled = flagClient.getBooleanValue("miyu.layer.enabled", false);
```

## 14. 性能
| 度量 | 目标 |
|------|------|
| 首屏 LCP | <2.5s |
| JS Bundle (初始) | <300KB gz |
| WS Re-render | 每秒≤10 次 |

## 15. 测试
- 单元：vitest
- 组件：@testing-library/react
- E2E：Playwright/Cypress

## 16. 常见错误
| 错误 | 解决 |
|------|------|
| Realtime 重复订阅 | 在 useEffect 清理 |
| 大图谱卡顿 | Graph 虚拟化 + 分块渲染 |
| Emotion 抖动 | 前端加平滑阈值 |
