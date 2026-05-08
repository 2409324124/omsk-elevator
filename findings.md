# 发现与决策

## 需求
- 项目目标是制作 20-30 分钟的《电梯向下》TNO 鄂木斯克同人自适应视觉小说 Demo。
- 玩家身份是美国参访团随团翻译；场景限定在外宾接待楼、电梯、地上楼层和地下层。
- 叙事必须渐进式披露：不在开局揭示真实意识形态、地下设施用途、监控与宣传/情报对象关系。
- 系统必须状态驱动：选择更新玩家状态、热度、证据和 flag，再影响后续 scene 出现概率与结局 basin。
- 当前优先级是 CLI 原型、scene JSON、NumPy router，再考虑 Ren'Py/Web/LLM。

## 研究发现
- 当前项目已有核心文档：`AGENTS.md`、`README.md`、`03_adaptive_router_and_statistics.md`、`05_scene_schema_and_scene_bank_examples.md`、`06_demo_flow_20_30min.md`、`07_local_agent_workflow.md`。
- 当前已存在最小代码骨架：`engine/state.py`、`engine/schema.py`、`engine/update.py`、`scripts/validate_scenes.py`。
- 已新增轻路由与 CLI：`engine/router.py`、`scripts/run_cli_demo.py`。
- 已新增最小 scene 数据：`data/scenes/demo_intro.json`，包含 5 个 scene，并能进入地下动态 scene。
- 已新增容器运行链路：`requirements.txt`、`Dockerfile`、`docker-compose.yml`、`.dockerignore`。
- 宿主机有 Docker / Docker Compose，但宿主 Python 环境缺少 NumPy；容器运行是当前可靠路径。
- IPIP 官方站点提供 Johnson IPIP-NEO-120 条目页，并说明其为 120-item public domain inventory。
- `NeuroQuestAi/five-factor-e` 提供 IPIP-NEO-120 的 `questions.json`，项目许可证为 MIT。
- 已下载 120 条 questions raw JSON 到 `data/reference/ipip_neo_120/questions_raw.json`，仅作参考层，不进入游戏 scene。
- 8values 仓库 `8values/8values.github.io` 标识为 MIT License；本项目只保存白名单文件 `questions.js` 与 `LICENSE` 的参考副本。
- 8values 只用于参考 `econ/dipl/govt/scty` 四个价值轴，不用于现实政治画像或政治意识形态输出。
- `scripts/extract_reference_constructs.py` 可输出 reference-only 摘要：IPIP 题数、映射构念、8values 轴权重统计；脚本会检查输出中不得包含 raw item text。
- 交叉审阅结论为“有条件通过”：引擎骨架、参考层、CLI 入口可用，但还不是可发布最小 Demo。
- 交叉审阅确认阻塞项：缺少 `engine/ending.py`、缺少 `data/scenes/endings.json`、scene 数量仅 5 个且低于验收要求。
- 交叉审阅确认高优先级修复项：`router.py` 里 `_unresolved_thread_score` 硬编码 flag，`validate_scenes.py` 未校验 `hidden_constructs`。
- `validate_scenes.py` 已补 `hidden_constructs` 值域检查，非法值会报出 scene id 和 construct 名。
- `engine/ending.py` 已实现 6 个 ending basin；CLI 在 MAX_STEPS 后会显示数值系统选出的结局。

## 技术决策
| 决策 | 理由 |
|------|------|
| `PlayerState.theta` 使用 dict | 与文档中的构念名直连，便于 scene JSON effects 更新 |
| `apply_choice` 使用 NumPy 做均值回归 | 满足“尽量使用 NumPy”，同时保持逻辑简单 |
| `surveillance_heat` 和 `evidence_count` 不回归 | 文档明确这些是粘性事件变量 |
| `router` 使用 softmax 抽样 | 符合过程随机、后期收束的路线 |
| `validate_scenes.py` 先做基础校验 | 当前阶段避免过度 schema 收紧，给 scene bank 扩展留空间 |
| Docker 镜像只安装 NumPy | 避免 PyTorch 轮子把原型复杂度带偏 |
| IPIP-NEO-120 只作构念参考 | 避免凭空编题库，同时避免把公开量表原题直接变成游戏文本 |
| 8values 只作价值轴参考 | 后续把政治价值冲突改造成鄂木斯克场景压力测试，不输出现实政治标签 |
| 提取脚本只输出元数据和统计 | 防止公开题项直接流入游戏 scene 或玩家可见文本 |
| 结局系统优先于扩 scene 和模拟 | 没有 ending evaluator 时，basin_pressure 是死数据，模拟也无法验证结局分布 |
| 结局系统只用 PlayerState 数值 | 防止 LLM 或叙事文本参与结局判定 |

## 遇到的问题
| 问题 | 解决方案 |
|------|---------|
| 指定文档路径曾与实际项目根目录不一致 | 按同名文件在项目根目录读取 |
| 宿主机没有 `python` 命令 | 使用 `python3` |
| 宿主机缺 NumPy | 用 Docker 固定依赖并执行 CLI/校验 |
| CLI 脚本直接运行时找不到 `engine` 包 | 在 `scripts/run_cli_demo.py` 加入项目根目录到 `sys.path` |

## 资源
- 本项目规划文件：`task_plan.md`、`findings.md`、`progress.md`
- GitHub 公开仓库：`https://github.com/2409324124/omsk-elevator`
- IPIP 官方：`https://ipip.ori.org/`
- Johnson IPIP-NEO-120：`https://ipip.ori.org/30FacetNEO-PI-RItems.htm`
- Five Factor E：`https://github.com/NeuroQuestAi/five-factor-e`
- IPIP-NEO-120 questions JSON：`https://raw.githubusercontent.com/NeuroQuestAi/five-factor-e/main/data/IPIP-NEO/120/questions.json`
- 8values 仓库：`https://github.com/8values/8values.github.io`
- 8values README：`https://github.com/8values/8values.github.io/blob/master/README.md`
- 8values LICENSE：`https://github.com/8values/8values.github.io/blob/master/LICENSE`
- 8values questions.js：`https://github.com/8values/8values.github.io/blob/master/questions.js`
- Reference-only 提取脚本：`scripts/extract_reference_constructs.py`
- 交叉审阅报告：`docs/reviews/cross_review_2026-05-08.md`
- 结局系统：`engine/ending.py`
- 结局数据：`data/scenes/endings.json`
- 技能文件：`/home/miku/.codex/skills/planning-with-files-zh/SKILL.md`
- 技能模板：`/home/miku/.codex/skills/planning-with-files-zh/templates/`
- 可借鉴远端轮子：`2409324124/adaptive_psych_system` 的 Docker/Compose 和 session/progress 思路；不直接搬 PyTorch IRT。

## 视觉/浏览器发现
- 未使用浏览器或图片工具。

---
*每执行2次查看/浏览器/搜索操作后更新此文件*
*防止视觉信息丢失*
