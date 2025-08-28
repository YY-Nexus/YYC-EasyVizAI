# 设计 Tokens 与体验系统

## 1. Token 分类

| 类别 | 示例 |
|------|------|
| color | --color-ink |
| spacing | --space-2 --space-4 |
| motion | --motion-fast |
| typography | --font-size-base |
| sound | enter / emotion_shift |
| emotion mapping | stressed → palette calm-soft |

## 2. 生成流程

1. 编辑 `design-system/tokens/base.json`
2. 运行 `pnpm tokens:build`
3. 输出：
   - `dist/tokens.css`
   - `dist/tokens.ts`
   - `dist/sound-manifest.json`

## 3. Emotion 映射

```json
{
 "stressed": { "palette": "soft", "motion": "reduced", "sound": "breath_pad" },
 "encouraged": { "palette": "vibrant", "motion": "dynamic", "sound": "sparkle" }
}
```

## 4. 动画层

- 基于 Framer Motion + Lottie
- 动画强度与 emotion 绑定
- 用户“减少动效模式” → 统一降级

## 5. 声效策略

| 场景 | 声音 |
|------|------|
| 进入应用 | welcome.mp3 |
| Section 完成 | soft_ding.mp3 |
| Emotion 切换 | breath_pad.mp3 |

懒加载：首次触发再导入。
