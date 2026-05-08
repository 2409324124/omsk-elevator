# 交叉审阅报告：《电梯向下》

审阅日期：2026-05-08  
审阅文件：README.md / AGENTS.md / engine/*.py / scripts/*.py / docs/references/*.md / data/reference/**/construct_mapping_draft.json / data/scenes/demo_intro.json

---

## 总体结论

**有条件通过**

引擎骨架正确，参考层完整，许可证边界清晰。但缺少 `engine/ending.py`、结局数据和模拟脚本，场景数量（5）距验收标准（≥20）差距明显。在补充场景和结局之前，不能视为可发布的最小 Demo。

---

## 当前项目阶段判断

> **可玩 CLI 阶段（入口）**：引擎骨架和 CLI 已就位，5 个 scene 可跑通，但场景池太小，结局系统未实现，尚未达到 20-30 分钟体验。

---

## 已完成项

1. **PlayerState dataclass** — 7 个 theta 维度 + surveillance_heat + evidence_count + relationships + flags + visited_scenes，字段设计合理。
2. **Scene / Choice / Ending / Preconditions schema** — `from_dict` 工厂方法、`extra` 兜底字段、跨文件 strict=True zip，设计正确。
3. **apply_choice（update.py）** — theta 均值回归、heat/evidence 独立累计、relationships/flags 更新链路完整；heat 和 evidence **未被均值回归误伤**（顺序正确：先加 delta，回归只作用于 theta，heat/evidence 在回归后再加）。
4. **自适应路由器（router.py）** — 支持 4 个阶段参数、preconditions 全字段、softmax temperature、重复惩罚、basin_pressure 聚合；`get_valid_scenes` 在外部过滤已访问场景，`choose_next_scene` 不会重复推送。
5. **场景验证器（validate_scenes.py）** — 覆盖 scene id 重复、choice id 重复、effects 合法键名和类型、force_next_if 跨文件场景引用。
6. **参考构念提取（extract_reference_constructs.py）** — 输出 `raw_item_text_emitted: false`；内置 `assert_no_item_text` 断言，防止原题泄露进输出；运行通过，无报错。
7. **参考层文档（docs/references/*.md）** — IPIP 和 8values 许可证来源、禁止用途、转译规则全部写明。
8. **construct_mapping_draft.json（IPIP + 8values）** — 均含 `usage: reference_only_not_game_text` 和 `do_not_copy_items_into_scenes: true`，8values 保留 MIT License 副本。
9. **CLI Demo（scripts/run_cli_demo.py）** — 含场景验证、state 摘要、narratized 叙事反馈（无临床/政治标签）、forced_next_scene_id 条件评估，可运行完整 5-step 游玩。
10. **demo_intro.json（5 个 scene）** — 渐进式披露结构正确；第一场景无需 flag 前置、地下场景有 required_flags_any 限制；`basin_pressure` 已在关键选项上设置。

---

## 缺失项

| 缺失项 | 是否阻塞 Demo |
|---|---|
| `engine/ending.py` — 结局 basin 评估器，无法路由到任何结局 | **阻塞** |
| `data/scenes/endings.json` — 结局数据，6 个结局方向无一可触达 | **阻塞** |
| scene 数量不足 — 当前 5 个，验收要求 ≥20 | **阻塞**（体验时长） |
| `scripts/simulate_runs.py` — 平衡性模拟，缺少即无法验证结局分布 | 不阻塞但必要 |
| `engine/__init__.py` — 缺失，目前靠 sys.path 黑魔法工作，不可包安装 | 低风险但技术债 |
| `prototype/` 目录 — AGENTS.md 规划中的路径，完全未创建 | 不阻塞 |

---

## 必须修复问题

### 🔴 P0：`_unresolved_thread_score` 硬编码场景 flag（router.py L98-107）

```python
if "underground_hint" in scene.tags and (
    "saw_b1_button" in state.flags or "noted_b1_button" in state.flags
):
```

场景专用 flag 名写死在路由引擎里。一旦 flag 改名或新增地下线索，路由器静默失效，且没有任何报错。  
**修复方向**：从 scene.tags 驱动权重，不在 router 里枚举 flag 名；或把该映射外置到 scene JSON 的 `weight_hints` 字段。

---

### 🔴 P1：`validate_scenes.py` 未校验 `hidden_constructs`（validate_scenes.py L85-97）

validator 检查了 `effects` 的键是否合法，但**没有检查 `hidden_constructs` 是否都在 THETA_KEYS 内**。目前 demo_intro.json 引用了 `control_strategy` 等正确键，但若写错拼写，router 会用错误的 theta 键调用 `state.theta.get(key, 0.0)` 返回 0，静默失败，info_gain 计算偏低。  
**修复**：在 validate_scenes.py 加一行对 `hidden_constructs` 值域的校验。

---

### 🟡 P2：`apply_choice` 中新增 delta 在同一步被回归（update.py L15-21）

```python
state.theta[key] += delta          # 先加
theta_values = theta_values * rate # 然后整体回归，包括刚加的 delta
```

新选择产生的 delta 在同一步被乘以 0.85，导致收敛上界比预期低（上界 = delta/(1-rate) = 5.67 而非 6.67）。这不是运行错误，但与大多数 CAT/IRT 均值回归的惯例不符（通常只回归"旧状态"，新 delta 下一轮才参与回归）。  
**修复方向**：调换顺序 — 先对旧 theta 回归，再加新 delta。或保留现状但在文档中明确说明这是设计选择。

---

### 🟡 P3：`note_b1` 的 `force_next_if` 实际上几乎永远不触发

```json
"evidence_delta": 0.5,
"force_next_if": {"evidence_count_gte": 1.0, "scene": "b1_behavior_log_01"}
```

apply_choice 把 evidence_count 从 0 → 0.5，然后检查 ≥ 1.0 → False，跳过。只有玩家之前已收集 ≥ 0.5 证据时才能触发。若这是有意设计（"需要先收集证据才进地下"），需要在 JSON 注释或文档中标注。若是无意 bug，应把阈值改为 0.5 或把 evidence_delta 改为 1.0。

---

## 建议优化

1. **给 validate_scenes.py 加 `hidden_constructs` 合法性检查** — 5 行代码，防止静默失败，改动最小收益最大。
2. **把 `_unresolved_thread_score` 的 flag 名外置** — 可在 scene JSON 加一个可选 `router_weight_bonus` 字段，让 router 读 JSON 而不是硬编码 flag 名。
3. **补 `engine/__init__.py`（空文件即可）** — 消除 sys.path 黑魔法，使 `python3 -m engine.state` 和 pip install 正常工作。
4. **在 `apply_choice` 回归顺序上加内联注释** — 无论选择保留现状还是修复，都应在 L15 前加注释说明"回归应用于 delta 前/后的旧值"，避免下一个开发者误改。
5. **在 data/scenes/README.md 中补充 scene 数量进度追踪** — 目前只有 5/20+，加一行进度表帮助后续快速判断场景池是否达标。

---

## 已运行验证（宿主机静态）

| 命令 | 结果 |
|---|---|
| `python3 -m py_compile engine/state.py engine/schema.py engine/update.py engine/router.py scripts/validate_scenes.py scripts/extract_reference_constructs.py` | ✅ 全部通过，无语法错误 |
| `python3 scripts/extract_reference_constructs.py` | ✅ 正常输出 JSON，`raw_item_text_emitted: false`，未泄露原题 |
| `python3 scripts/validate_scenes.py data/scenes` | ✅ `OK: validated 5 scene(s)`，无错误 |
| `engine/ending.py` | ❌ 文件不存在 |
| `scripts/simulate_runs.py` | ❌ 文件不存在 |

---

## Docker 补充审阅（容器内运行时验证）

服务：`omsk-vn-cli`，镜像：`omsk-vn-cli:numpy`，挂载：`./` → `/app`

### 已运行命令与结果

| 命令 | 结果 |
|---|---|
| `python3 -m py_compile` 六个模块 | ✅ COMPILE_OK |
| `python3 scripts/extract_reference_constructs.py` | ✅ 正常，`raw_item_text_emitted: false` |
| `python3 scripts/validate_scenes.py data/scenes` | ✅ `OK: validated 5 scene(s)` |
| apply_choice 回归隔离测试 | ✅ `surveillance_heat: 5.5`、`evidence_count: 3.5`，均未被回归误伤 |
| `truth_seek` delta→回归后值 | ✅ `1.0 * 0.85 = 0.85`，数值链路正确 |
| Router preconditions 过滤 | ✅ `required_flags_any`/`forbidden_flags`/`min_choice_index`/`min_surveillance_heat` 全部正确过滤 |
| `force_next_if` 边界（情形A） | ✅ `evidence 0→0.5`，阈值 1.0，不触发，返回 `None` |
| `force_next_if` 边界（情形B） | ✅ `evidence 0.5→1.0`，阈值 1.0，触发 `b1_behavior_log_01` |
| Router `temperature=0` argmax | ✅ 正确选出高分 scene |
| Router softmax (`temperature=1.0`) | ✅ 返回非 None，不崩溃 |

### 运行时确认的 P2（回归顺序）

```
10步 truth_seek=4.551
理论上限（新 delta 被回归）≈ 5.667
理论上限（旧 delta 回归）≈ 6.667
```

10 步收敛路径朝向 5.667 方向，确认当前实现是"先加 delta 再整体回归"。行为一致，无崩溃。**是否调整顺序属设计取向问题，不是正确性 bug**，但建议在 `update.py` 加注释说明。

### 新增发现：无新 P0/P1

前一份报告的静态分析结论全部得到运行时验证确认，无需修改已有结论级别。

---

## 下一步建议

**优先级：补 `engine/ending.py`**

理由：
- 这是唯一阻塞"结局收束"机制的空缺。没有 ending evaluator，所有 `basin_pressure` 数据都是死数据，游戏只能无结局地跑完 MAX_STEPS 退出。
- 比补 scene 更优先：scene 可以线性增量增加，但没有结局系统，再多 scene 也无法完成"过程随机 → 结局收束"的核心设计承诺。
- 比补 `simulate_runs.py` 更优先：没有 `ending.py`，模拟脚本也无法测试结局分布。

`ending.py` 最小实现范围：
1. 读取 `data/scenes/endings.json`（Ending schema 已存在）
2. 根据 `PlayerState.theta`、`surveillance_heat`、`evidence_count`、`flags` 计算每个结局的激活分
3. 返回得分最高的结局（不允许 LLM 决定）
4. CLI Demo 在 MAX_STEPS 后调用 ending evaluator 显示结局文本
