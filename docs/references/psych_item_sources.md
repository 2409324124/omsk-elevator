# 心理题项参考源

本项目只把公开题项作为“构念结构参考层”，用于后续把心理构念改造成视觉小说里的剧情压力测试。不得把量表原题直接复制进游戏 scene，也不得把玩家路线解释成临床诊断。

## IPIP / IPIP-NEO-120

- 参考源名称：International Personality Item Pool / Johnson IPIP-NEO-120
- 来源 URL：
  - 官方 IPIP：<https://ipip.ori.org/>
  - Johnson IPIP-NEO-120 条目页：<https://ipip.ori.org/30FacetNEO-PI-RItems.htm>
- 许可证/使用说明摘要：
  - IPIP 是 public domain item pool。
  - Johnson IPIP-NEO-120 是 120-item public domain inventory，用于测量五大人格模型的 30 个 facet。
- 本项目如何使用：
  - 只借用 Big Five domain / facet 的构念结构。
  - 将构念转译成鄂木斯克封闭场景中的叙事压力：翻译取舍、风险承担、群体安全、本地共情、服从与控制策略。
  - 原题只可保存在 `data/reference/` 作为参考资料，不得进入 `data/scenes/`。
- 禁止用途：
  - 不得做临床诊断。
  - 不得输出心理疾病、人格障碍或“玩家患有某病”的判断。
  - 不得把 IPIP 原题作为游戏选项或旁白逐字呈现。

## NeuroQuestAi/five-factor-e

- 参考源名称：NeuroQuestAi/five-factor-e
- 来源 URL：
  - GitHub 项目：<https://github.com/NeuroQuestAi/five-factor-e>
  - IPIP-NEO-120 questions JSON：<https://raw.githubusercontent.com/NeuroQuestAi/five-factor-e/main/data/IPIP-NEO/120/questions.json>
- 许可证/使用说明摘要：
  - 项目代码使用 MIT License。
  - 项目 README 说明其基于 IPIP / IPIP-NEO，支持 120 题和 300 题版本。
- 本项目如何使用：
  - 优先参考 120 题版本的数据结构和题项覆盖范围。
  - 后续可从 `questions_raw.json` 中提取 domain / facet 结构，但必须转译为原创剧情压力测试。
  - 不直接接入 five-factor-e 的评分系统，不输出人格分数，不生成诊断。
- 禁止用途：
  - 不使用 300 题长版作为当前阶段输入。
  - 不把库输出的 “score” 或人格标签展示给玩家。
  - 不把玩家路线解释为心理疾病、临床风险或人格缺陷。

## 当前落地文件

- 原始参考题项：`data/reference/ipip_neo_120/questions_raw.json`
- 构念映射草稿：`data/reference/ipip_neo_120/construct_mapping_draft.json`

## 写作规则

后续写 scene 时必须遵守：

1. 先看构念和 facet，不复制原题文本。
2. 把心理题项转译为具体压力情境，例如监听、翻译偏差、证据携带、群体安全、地下求助。
3. 输出给玩家的只能是叙事化反馈，例如“你更倾向于用控制换取安全”，不能是心理诊断。
