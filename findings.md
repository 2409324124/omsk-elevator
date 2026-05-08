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

## 技术决策
| 决策 | 理由 |
|------|------|
| `PlayerState.theta` 使用 dict | 与文档中的构念名直连，便于 scene JSON effects 更新 |
| `apply_choice` 使用 NumPy 做均值回归 | 满足“尽量使用 NumPy”，同时保持逻辑简单 |
| `surveillance_heat` 和 `evidence_count` 不回归 | 文档明确这些是粘性事件变量 |
| `router` 使用 softmax 抽样 | 符合过程随机、后期收束的路线 |
| `validate_scenes.py` 先做基础校验 | 当前阶段避免过度 schema 收紧，给 scene bank 扩展留空间 |
| Docker 镜像只安装 NumPy | 避免 PyTorch 轮子把原型复杂度带偏 |

## 遇到的问题
| 问题 | 解决方案 |
|------|---------|
| 指定文档路径曾与实际项目根目录不一致 | 按同名文件在项目根目录读取 |
| 宿主机没有 `python` 命令 | 使用 `python3` |
| 宿主机缺 NumPy | 用 Docker 固定依赖并执行 CLI/校验 |
| CLI 脚本直接运行时找不到 `engine` 包 | 在 `scripts/run_cli_demo.py` 加入项目根目录到 `sys.path` |

## 资源
- 本项目规划文件：`task_plan.md`、`findings.md`、`progress.md`
- 技能文件：`/home/miku/.codex/skills/planning-with-files-zh/SKILL.md`
- 技能模板：`/home/miku/.codex/skills/planning-with-files-zh/templates/`
- 可借鉴远端轮子：`2409324124/adaptive_psych_system` 的 Docker/Compose 和 session/progress 思路；不直接搬 PyTorch IRT。

## 视觉/浏览器发现
- 未使用浏览器或图片工具。

---
*每执行2次查看/浏览器/搜索操作后更新此文件*
*防止视觉信息丢失*
