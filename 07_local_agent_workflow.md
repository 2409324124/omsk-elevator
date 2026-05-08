# 07 本地 Agent 工作流

## 1. 第一阶段：搭建数据结构

任务：

```text
创建 engine/state.py
创建 engine/schema.py
创建 data/scenes/*.json
```

实现：

```python
PlayerState
Scene
Choice
Ending
```

`PlayerState` 至少包含：

```text
theta: dict[str, float]
surveillance_heat: float
evidence_count: float
relationships: dict[str, float]
flags: set[str]
choice_index: int
visited_scenes: list[str]
```

## 2. 第二阶段：写状态更新器

任务：

```text
创建 engine/update.py
```

函数：

```python
apply_choice(state, choice) -> state
```

要求：

```text
连续变量应用均值回归。
surveillance_heat 不回归。
evidence_count 不回归。
flags 只增不减，除非 scene 明确允许移除。
relationship_effects 正常累加。
```

## 3. 第三阶段：写路由器

任务：

```text
创建 engine/router.py
```

函数：

```python
get_valid_scenes(state, scenes)
score_scene(scene, state, phase)
choose_next_scene(valid_scenes, state, phase)
```

要求：

```text
支持 preconditions。
支持 tags 重复惩罚。
支持 phase 参数。
支持 ending_basin_pressure。
支持 temperature 随阶段降低。
```

## 4. 第四阶段：写结局判定器

任务：

```text
创建 engine/ending.py
```

函数：

```python
compute_ending_scores(state)
choose_ending(state)
```

要求：

```text
支持硬条件 BE。
支持 softmax 概率。
支持最终阶段低温收束。
```

优先级：

```text
1. 硬触发 BE
2. 关键 flag 组合
3. ending_score 最大值
4. softmax 抽样
```

## 5. 第五阶段：写 scene 校验器

任务：

```text
创建 scripts/validate_scenes.py
```

检查：

```text
scene id 唯一
choice id 唯一
effects 字段合法
preconditions 引用合法
force_next_if 引用合法
ending basin 名称合法
```

## 6. 第六阶段：写模拟器

任务：

```text
创建 scripts/simulate_runs.py
```

用途：

```text
随机模拟 1000 次玩家路径。
统计各结局概率。
统计平均 surveillance_heat。
统计各 scene 出现频率。
检查是否存在永远无法触发的 scene。
检查是否某个 BE 过高频。
```

建议输出：

```text
ending distribution
average path length
top 10 most frequent scenes
dead scenes
overpowered choices
```

## 7. 第七阶段：写文本原型

先不要接复杂前端。

用 CLI 即可：

```text
显示 scene 文本
显示选项
输入编号
更新状态
选择下一 scene
直到结局
```

## 8. 第八阶段：接 Ren'Py 或 Web

推荐顺序：

```text
CLI 原型
Web 纯文本原型
Ren'Py 视觉小说原型
LLM 叙事润色
```

## 9. 本地 Agent 具体任务提示词

### 任务 1：创建状态系统

```text
请根据 docs/07_local_agent_workflow.md 和 docs/03_adaptive_router_and_statistics.md，创建 engine/state.py 和 engine/update.py。要求使用 dataclass，不依赖 PyTorch，优先使用 Python 标准库和 NumPy。实现 PlayerState、ChoiceEffect、apply_choice，并写最小单元测试。
```

### 任务 2：创建 scene schema

```text
请根据 docs/05_scene_schema_and_scene_bank_examples.md，创建 engine/schema.py，定义 Scene、Choice、Preconditions 的 dataclass 或 Pydantic 模型。再创建 scripts/validate_scenes.py，能校验 data/scenes 下所有 JSON。
```

### 任务 3：创建路由器

```text
请根据 docs/03_adaptive_router_and_statistics.md，创建 engine/router.py。实现 get_valid_scenes、score_scene、choose_next_scene。要求支持 phase 参数、temperature、重复惩罚、preconditions、ending_basin_pressure。
```

### 任务 4：创建结局系统

```text
请根据 docs/06_demo_flow_20_30min.md 和 docs/03_adaptive_router_and_statistics.md，创建 engine/ending.py。实现 6 个 ending basin 的线性打分，并支持 surveillance_heat >= 7 时硬触发 BE_missing_tourist。
```

### 任务 5：创建样例场景

```text
请根据 docs/05_scene_schema_and_scene_bank_examples.md 和 docs/06_demo_flow_20_30min.md，在 data/scenes 中创建至少 20 个 scene JSON。要求包含地上层 6 个、B1 6 个、B2 6 个、晚餐/结局前 2 个。
```

### 任务 6：创建 CLI Demo

```text
请创建 prototype/cli_demo.py，加载 data/scenes，初始化 PlayerState，按顺序执行前 3 个固定 scene，从第 4 个开始调用 router，直到 ending.py 返回结局。每次选择后打印关键 debug 信息，但 debug 默认关闭。
```

### 任务 7：模拟平衡性

```text
请创建 scripts/simulate_runs.py，随机模拟 1000 次游戏，输出各结局分布、平均路径长度、平均 surveillance_heat、最常出现 scene、从未出现 scene。根据结果指出哪些 choice 或 scene 过强。
```

## 10. 验收清单

最小可用版本必须满足：

```text
[ ] 可以从 CLI 跑完一局
[ ] 至少 20 个 scene
[ ] 至少 12 个关键选择
[ ] 至少 6 个结局
[ ] D 选项“私下告诉记者”不会立刻死，但会显著增加失踪 BE 概率
[ ] 第 1-3 个选择固定
[ ] 第 4-5 个选择轻量自适应
[ ] 第 6 个选择后路由器正式工作
[ ] 有均值回归
[ ] 有 surveillance_heat
[ ] 有 evidence_count
[ ] 有 ending basin 线性打分
[ ] 有 scene 校验脚本
[ ] 有模拟脚本
```
