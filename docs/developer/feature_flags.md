# Feature Flags & 实验

## 1. 用途

- 灰度发布（Miyu、报告分段）
- A/B 情感主题映射
- 模型版本切换

## 2. 客户端使用（示例）

```ts
const ffClient = useOpenFeature();
const isMiyu = ffClient.getBooleanValue("miyu.layer.enabled", false);
```

## 3. Flag 定义（YAML 或 JSON）

```
miyu.layer.enabled:
  type: boolean
  variants: [on, off]
  rules:
    - attribute: user.role
      equals: pro
      serve: on
```

## 4. 评估流程

1. 请求 /api/v1/flags
2. 缓存 5 分钟
3. 本地求值（OpenFeature）

## 5. A/B 数据埋点

事件：`feature.flag.evaluated`

- 属性：flag_id, variant, user_segment

## 6. 实验关闭

- 复制优胜 variant → 写入默认规则
- 删除其他 variant → 清理 dashboard

## 7. 反模式

| 场景 | 说明 |
|------|------|
| Flag 永久不清理 | 复杂度上升 |
| 业务逻辑跨层级散落判断 | 用 central helper |
| Flag 命名不语义 | 使用 domain + purpose |
