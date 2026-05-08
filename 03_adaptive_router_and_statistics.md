# 03 自动剧情路由与统计机制

## 1. 什么时候启动自动选择系统？

推荐规则：

```text
第 1-3 个关键选择：固定采样，只记录状态，不改变主线。
第 4-5 个关键选择：轻量自适应，改变台词、座位、角色态度。
第 6-9 个关键选择：正式启动自动剧情路由。
第 10-12 个关键选择：降低随机性，开始强收束。
最终选择：根据 ending_score 和关键 flag 进入结局。
```

不要第 1 个选择就正式启动路由。

原因：

```text
早期选择噪声很大。
玩家可能只是试选项，不代表稳定倾向。
过早自适应会误判玩家。
```

## 2. 状态更新

推荐使用 NumPy 即可。

伪代码：

```python
def update_state(state, choice):
    # 连续型心理/行为倾向
    state.theta += choice.effect_vector

    # 均值回归，避免一次选择过拟合
    state.theta = state.theta * state.regression_rate

    # 粘性变量，不回归
    state.surveillance_heat += choice.heat_delta
    state.evidence_count += choice.evidence_delta

    # 关系变量
    for k, v in choice.relationship_effects.items():
        state.relationships[k] += v

    # 事件 flag
    for flag in choice.flags:
        state.flags.add(flag)

    return state
```

## 3. 均值回归

均值回归用于防止单个选项毁掉整局。

推荐：

```text
theta = 0.85 * theta
```

或：

```text
theta = 0.85 * theta + 0.15 * prior
```

其中 `prior` 通常是零向量。

### 可回归变量

```text
truth_seek
risk_tolerance
authority_compliance
local_empathy
self_preservation
control_strategy
```

### 不可回归变量

```text
surveillance_heat
evidence_count
forbidden_area_seen
identity_exposed
reporter_has_proof
guide_compromised
```

原因：

```text
性格倾向可以被后续行为修正。
但已经被监听、偷拿证据、进入禁区，这些事件不会自然消失。
```

## 4. 线性模型预测结局分数

使用线性模型计算各结局 basin 的分数：

```text
ending_score = W @ features + b
```

示例：

```python
features = [
    truth_seek,
    group_safety,
    local_empathy,
    authority_compliance,
    self_preservation,
    risk_tolerance,
    control_strategy,
    surveillance_heat,
    evidence_count,
    reporter_trust,
    guide_trust,
]
```

### 示例结局分数

```text
evidence_escape =
  +1.2 * truth_seek
  +1.0 * group_safety
  +1.0 * evidence_count
  -0.8 * surveillance_heat

safe_exit =
  +1.0 * self_preservation
  +0.8 * authority_compliance
  -0.5 * evidence_count
  -0.6 * surveillance_heat

missing_tourist =
  +1.5 * surveillance_heat
  +0.8 * truth_seek
  +0.6 * reporter_trust
  -0.5 * authority_compliance

collaborator =
  +1.1 * self_preservation
  +1.0 * control_strategy
  +0.7 * authority_compliance
  -0.6 * local_empathy

sacrifice_stay =
  +1.2 * local_empathy
  +1.0 * group_safety
  -1.0 * self_preservation
```

## 5. Softmax 概率收束

不要过早硬判结局。

先计算各结局概率：

```python
def softmax(scores, temperature=1.0):
    x = scores / temperature
    x = x - x.max()
    e = np.exp(x)
    return e / e.sum()
```

前期温度高，结果更随机。

后期温度低，结果更确定。

推荐：

```text
前期 temperature = 1.2
中期 temperature = 0.7
后期 temperature = 0.2
```

## 6. Scene 选择公式

每个候选 scene 的分数：

```text
score(scene) =
  α * info_gain
+ β * narrative_fit
+ γ * unresolved_thread
+ δ * ending_basin_pressure
+ ε * random_noise
- λ * repetition_penalty
```

### 各项解释

```text
info_gain：
该 scene 是否能区分玩家尚不确定的倾向。

narrative_fit：
该 scene 是否符合当前楼层、角色在场、剧情节奏。

unresolved_thread：
该 scene 是否能回应之前埋下的伏笔。

ending_basin_pressure：
该 scene 是否会把玩家推向当前最可能的结局 basin。

random_noise：
少量随机性，让过程不同。

repetition_penalty：
避免连续出现同类拷问。
```

## 7. 阶段参数

```python
PHASES = {
    "surface_fixed": {
        "alpha": 0.0,
        "beta": 1.0,
        "gamma": 0.5,
        "delta": 0.0,
        "temperature": 0.0,
    },
    "early_adaptive": {
        "alpha": 0.4,
        "beta": 1.0,
        "gamma": 0.7,
        "delta": 0.2,
        "temperature": 1.0,
    },
    "underground_router": {
        "alpha": 1.0,
        "beta": 1.0,
        "gamma": 0.8,
        "delta": 0.5,
        "temperature": 0.7,
    },
    "ending_converge": {
        "alpha": 0.5,
        "beta": 0.8,
        "gamma": 0.5,
        "delta": 1.5,
        "temperature": 0.2,
    },
}
```

## 8. Fisher 信息可选机制

如果要接入项目原有的 CAT / IRT 思路，可以把 scene 看成测量题。

每个 scene 有一个 discrimination 向量 `a`，表示它主要区分哪些维度。

对二分类近似：

```text
p = sigmoid(a · theta)
Fisher = p * (1 - p) * outer(a, a)
```

直觉：

```text
当玩家在某个冲突上最不确定时，该 scene 信息量最大。
```

实际 Demo 可以先不用完整 IRT，只用 `info_gain = uncertainty_weight * scene_discrimination` 的简化版。

## 9. 延迟 BE 机制

不要让危险选项立刻死亡。

使用 delayed bad ending：

```text
选择危险行为 -> 增加 surveillance_heat
后续继续危险 -> 进入高危池
晚餐或卫生间触发 BE
结尾回放前面埋下的线索
```

示例：

```python
if state.surveillance_heat >= 7:
    force_scene("BE_missing_tourist")
elif state.surveillance_heat >= 5:
    add_candidate("dinner_second_glass", weight=3.0)
```

## 10. 玩家可接受的随机性

玩家可以接受：

```text
我做了危险行为，所以危险剧情更容易出现。
```

玩家不能接受：

```text
我什么都没做，突然被剧情杀。
```

所以所有随机选择都必须能被事后解释。
