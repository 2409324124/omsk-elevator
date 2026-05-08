# 任务计划：《电梯向下》自适应 VN CLI 原型

## 目标
将 TNO 鄂木斯克同人视觉小说 Demo 从概念文档推进为可运行、可验证、可扩展的 NumPy 自适应 CLI 原型，并保持渐进式披露与状态驱动路由原则。

## 当前阶段
阶段 6

## 各阶段

### 阶段 1：项目边界与核心约束
- [x] 阅读项目根规则与指定设计文档
- [x] 确认叙事边界：不提前揭示真相、不做固定分支树、不输出心理诊断
- [x] 确认技术边界：Python 标准库 + NumPy，不接 PyTorch / LLM / Ren'Py / Web
- **状态：** complete

### 阶段 2：最小数据与状态骨架
- [x] 创建 `PlayerState`
- [x] 创建 `Choice` / `Scene` / `Preconditions` / `Ending` dataclass schema
- [x] 创建 `apply_choice`
- [x] 创建基础 scene validator
- **状态：** complete

### 阶段 3：轻路由 CLI + Docker 原型
- [x] 创建 NumPy 轻量 router
- [x] 创建 5 个最小 demo scene
- [x] 创建可交互 CLI
- [x] 创建 `requirements.txt` / `Dockerfile` / `docker-compose.yml`
- [x] 完成容器内校验和 5 步 CLI 冒烟
- **状态：** complete

### 阶段 4：项目整理与持久化规划
- [x] 启用 `planning-with-files-zh`
- [x] 创建 `task_plan.md`
- [x] 创建 `findings.md`
- [x] 创建 `progress.md`
- [x] 后续任务开始前先读取三个规划文件
- **状态：** complete

### 阶段 4.1：GitHub 仓库发布
- [x] 初始化本地 git 仓库
- [x] 创建 `.gitignore`
- [x] 提交当前 CLI 原型
- [x] 创建 GitHub 仓库 `2409324124/omsk-elevator`
- [x] 将仓库可见性改为 public
- [x] 推送 `main` 分支并设置 upstream
- **状态：** complete

### 阶段 4.2：公开心理题项参考层
- [x] 创建 `data/reference/`
- [x] 创建 `data/reference/ipip_neo_120/`
- [x] 创建 `docs/references/`
- [x] 记录 IPIP / IPIP-NEO-120 与 `NeuroQuestAi/five-factor-e` 来源说明
- [x] 下载 IPIP-NEO-120 questions JSON 到参考层
- [x] 创建构念映射草稿，明确不得复制题项进 scene
- **状态：** complete

### 阶段 4.3：意识形态/政治价值观参考层
- [x] 只使用 `8values/8values.github.io` 白名单文件
- [x] 下载 `questions.js` 到参考层
- [x] 下载 `LICENSE` 到参考层
- [x] 创建 `SOURCE.md`
- [x] 创建意识形态轴到游戏价值冲突的映射草稿
- [x] 创建参考源说明文档
- [x] 确认未修改 engine、scene、UI 或 LLM 相关文件
- **状态：** complete

### 阶段 4.4：reference-only 提取脚本
- [x] 创建 `scripts/extract_reference_constructs.py`
- [x] 输出 IPIP-NEO-120 与 8values 的统计摘要
- [x] 统计 8values 四轴权重覆盖
- [x] 输出构念映射概览
- [x] 主动检查并阻止原题文本出现在输出中
- [x] 提交并推送 reference 更新到 GitHub
- **状态：** complete

### 阶段 4.5：交叉审阅同步
- [x] 读取 `docs/reviews/cross_review_2026-05-08.md`
- [x] 记录总体结论：有条件通过
- [x] 记录阻塞项：缺少 `engine/ending.py`、`data/scenes/endings.json`、scene 数量不足
- [x] 记录高优先级修复项：router flag 硬编码、validator 未校验 `hidden_constructs`
- [x] 将下一步优先级调整为先补结局系统
- **状态：** complete

### 阶段 4.6：审阅小修复
- [x] `validate_scenes.py` 校验 `hidden_constructs`
- [x] 非法 hidden construct 报出 scene id 和 construct 名
- [x] 未修改 `router.py`
- [x] 未修改 `engine/update.py`
- [x] 未新增 scene
- **状态：** complete

### 阶段 5：结局系统
- [x] 创建 `engine/ending.py`
- [x] 创建 `data/scenes/endings.json`
- [x] 用 NumPy 实现 ending basin 线性打分
- [x] 支持 `surveillance_heat >= 7` 硬触发 `missing_tourist`
- [x] CLI 在 MAX_STEPS 后调用 ending evaluator 显示结局文本
- [x] 添加最小验证入口
- **状态：** complete

### 阶段 5.1：结局 flags 与回归测试
- [x] 让 `state.flags` 明确参与普通 ending basin 打分
- [x] 未配置 flag 默认忽略，不阻塞 scene 增量扩展
- [x] `load_endings()` 校验 6 个 basin 完整性
- [x] 新增标准库 `unittest` 覆盖 hard BE、flags bonus、缺失 key 容错和 basin 可选中性
- **状态：** complete

### 阶段 6：扩展到 12 个关键选择
- [ ] 将 scene 扩展到 12 个关键选择
- [ ] 至少包含 1 个延迟触发 BE
- [ ] 至少包含 1 个反直觉但公平的死亡/失踪路线
- [ ] 至少包含 1 个按状态动态出现的地下 scene
- **状态：** pending

### 阶段 7：测试与模拟
- [ ] 给 `apply_choice` 添加单元测试
- [ ] 给 `router` 添加单元测试
- [ ] 创建轻量 `scripts/simulate_runs.py`
- [ ] 统计结局分布、平均热度、scene 出现频率
- **状态：** pending

## 关键问题
1. 结局系统第一版是否只做 5 个结局 basin，还是直接包含文档中的 6 个方向？
2. scene 数据是否继续集中在 `demo_intro.json`，还是下一阶段拆分为 `act1_surface.json`、`act2_b1.json` 等文件？
3. CLI 是否需要非交互模式参数，方便后续自动测试与模拟复用？
4. `_unresolved_thread_score` 的 flag 权重映射是先外置到 JSON，还是先降级为纯 tag 驱动？

## 已做决策
| 决策 | 理由 |
|------|------|
| 先用 NumPy，不接 PyTorch | 当前 VN 路由只需要轻量数值计算，PyTorch 会过早增加镜像和系统复杂度 |
| LLM 不参与数值决策 | 遵守项目规则：LLM 只能润色文本，不能决定结局或篡改状态 |
| CLI 先跑 5 步 | 足够验证 scene 加载、选择、状态更新、动态地下 scene 与 Docker 链路 |
| Docker 默认运行 CLI | 宿主机缺 NumPy，容器能固定依赖并降低环境差异 |
| 状态摘要叙事化输出 | 避免心理诊断式标签，符合项目心理学边界 |
| GitHub 仓库设为 public | 用户明确要求公开仓库，便于外部查看与协作 |
| 新增参考题库层，不写入 scene | 用户明确要求不要凭空编心理题库，也不要把原题直接写入游戏 |
| 8values 只作价值轴参考 | 用户明确要求不要做现实政治倾向测评，也不要复制题目进 scene |
| reference 提取脚本不输出原题文本 | 参考题库只能辅助构念设计，不能把量表题目转成游戏内容 |
| 先补 `engine/ending.py` | 交叉审阅指出结局系统是当前阻塞“过程随机 → 结局收束”的最大缺口 |
| `hidden_constructs` 与 `THETA_KEYS` 对齐 | 避免 scene 拼写错误导致 router 静默按 0 处理构念 |
| 结局由数值系统决定 | 遵守 LLM 不决定结局、不篡改状态的核心边界 |
| flags 作为 ending bonus | flags 表示不可自然消失的事件痕迹，适合作为结局 basin 的附加分 |

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|---------|---------|
| 宿主机 `python` 不存在 | 1 | 使用 `python3` |
| 宿主机 Python 缺少 NumPy | 1 | 用 Docker 安装并运行 NumPy 依赖 |
| `python scripts/run_cli_demo.py` 找不到 `engine` | 1 | 在 CLI 入口将项目根目录加入 `sys.path` |
| `gh repo edit` 不支持 `--accept-visibility-change-consequences` | 1 | 改用当前版本支持的 `gh repo edit ... --visibility public` |
| `python -m py_compile scripts/validate_scenes.py` 中 `python` 不存在 | 1 | 记录失败原因，并用 `python3 -m py_compile scripts/validate_scenes.py` 完成等价校验 |
| 宿主机运行 `engine.ending` 时缺少 NumPy | 1 | 用 Docker 容器执行运行时硬触发检查 |

## 备注
- 重大实现前重新读取 `task_plan.md`、`findings.md`、`progress.md`。
- 所有外部资料只写入 `findings.md`，不要写入 `task_plan.md`。
- 每个阶段完成后更新阶段状态，并在 `progress.md` 记录验证命令。
