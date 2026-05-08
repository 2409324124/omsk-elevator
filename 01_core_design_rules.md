# 01 核心设计规则

## 1. 项目类型

本项目不是传统 Galgame，也不是纯 LLM 跑团。

本项目是：

> 基于自适应叙事推断的开放解法视觉小说。

玩家每次选择不只是进入一个分支，而是更新一组隐藏状态变量。

## 2. 核心循环

```text
展示 scene
玩家选择
更新玩家状态
更新监控热度
更新证据/关系/flag
计算候选 scene 权重
选择下一 scene
重复，直到进入结局 basin
```

## 3. 玩家状态向量

推荐初始维度：

```text
truth_seek            真相执念
group_safety          团队保护
local_empathy         本地共情
authority_compliance  权威服从
self_preservation     自我保全
risk_tolerance        风险承受
control_strategy      操控倾向
moral_fairness        公平感
```

可选扩展：

```text
loyalty_binding       群体忠诚
universalism          普遍主义
contamination_sense   污染/纯洁敏感
trust_calibration     信任校准能力
```

## 4. 重要隐藏变量

### surveillance_heat：监控热度

表示玩家是否已经被鄂木斯克系统识别为风险节点。

它不是人格变量，而是剧情风险变量。

例子：

```text
未经授权翻译硬标语：+1
私下提醒记者：+2
帮记者藏胶卷：+2
询问地下设施：+2
拿走观察表：+3
试图联系外界：+3
表面配合：-1
主动交出胶卷：-2
```

### evidence_count：证据数量

表示玩家掌握了多少可以带出建筑的证据。

例子：

```text
记住被删改标语：+0.5
拿到翻译稿残页：+1
拍下观察表：+2
藏起胶卷：+2
获得广播模板：+3
```

### trust variables：关系变量

```text
reporter_trust
guide_trust
major_suspicion
tour_group_stability
local_contact_trust
```

## 5. 结局不是固定分支，而是 basin

结局方向是吸引盆地，不是单一选项。

推荐 basin：

```text
safe_exit             安全离开
evidence_escape       带证据离开
missing_tourist       神秘失踪
collaborator          成为共犯
sacrifice_stay        牺牲留下
underground_stranded  地下滞留
```

## 6. 反直觉设计规则

允许出现反直觉选项。

例如：

```text
D. 私下告诉记者：这里的标语比她说的更硬。
```

这个选项在普通 VN 中像“正确路线”，但在本项目中可能导致高危。

原因：

```text
1. 玩家证明自己听懂了官方话术和真实俄文的差异。
2. 玩家证明自己愿意绕过官方渠道传播差异。
3. 玩家连接了记者这个外部传播节点。
```

但是不能无提示剧情杀。

必须提前埋线索：

```text
摄像头红光
导游修正翻译
少校关注玩家
翻译稿规定标准答案
记者已被重点观察
```

## 7. 禁止过度解释

错误写法：

```text
你意识到自己已经被监控了。
```

正确写法：

```text
你说完那句话后，导游没有回头。
但墙角黑色玻璃罩里，一点红光闪了一下。
```

## 8. Demo 的核心体验

玩家的体验应该是：

```text
我一开始以为自己只是翻译。
后来发现每个词都在决定谁能活着离开。
```
