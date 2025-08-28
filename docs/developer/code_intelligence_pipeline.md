# 代码智能解析流程

## 1. 阶段

| 阶段 | 描述 | 产出 |
|------|------|------|
| scanning | 文件枚举/过滤 | 元数据 |
| ast_build | 语言解析 AST | AST JSON |
| graph_layout | 调用/依赖图构建 | 边/节点 |
| enriching | 注释 / 复杂度统计 | 扩展属性 |
| done | 聚合输出 | graph.json |

## 2. 任务状态

queued → scanning → ast_build → graph_layout → enriching → done

## 3. 解析组件

- Adapter：Python / JS / Go 单独适配
- GraphBuilder：生成 call_graph
- ComplexityAnalyzer：评估圈复杂度

## 4. 结果缓存

key=`hash(language + sorted_file_hashes)`

- 命中 → 跳过阶段
- 失效策略：7d 清理

## 5. 数据结构（片段）

```json
{
 "nodes":[{"id":"func_main","label":"main","lang":"py"}],
 "edges":[{"from":"func_main","to":"func_helper","type":"call"}]
}
```

## 6. 安全

- 禁止执行：仅语法解析
- 大文件上限：单文件 < 300KB / 总行数 < 50k（可配置）

## 7. 指标

| 指标 | 描述 |
|------|------|
| code_analysis_stage_time_seconds | 各阶段耗时 |
| code_analysis_fail_total | 失败总数 |
| code_cache_hit_ratio | 缓存命中率 |
