# 05 Scene 数据结构与样例题库

## 1. Scene 基本结构

推荐 JSON 格式：

```json
{
  "id": "surface_slogan_translation_01",
  "act": 1,
  "location": "1F_lobby",
  "phase": "surface_fixed",
  "title": "大厅标语",
  "visible_text": "大厅墙上写着：纪律带来生存。",
  "hidden_constructs": [
    "truth_seek",
    "authority_compliance",
    "self_preservation"
  ],
  "preconditions": {
    "required_flags": [],
    "forbidden_flags": []
  },
  "choices": [],
  "tags": [
    "translation",
    "surface",
    "first_signal"
  ]
}
```

## 2. Choice 基本结构

```json
{
  "id": "tell_reporter_harder_slogan",
  "text": "私下告诉记者：这里的标语比她说的更硬。",
  "effects": {
    "truth_seek": 0.8,
    "risk_tolerance": 0.6,
    "authority_compliance": -0.5
  },
  "heat_delta": 2.0,
  "evidence_delta": 0.0,
  "relationship_effects": {
    "reporter_trust": 1.0,
    "major_suspicion": 1.0
  },
  "flags_add": [
    "unauthorized_translation_to_reporter"
  ],
  "basin_pressure": {
    "missing_tourist": 1.5,
    "evidence_escape": 0.5
  }
}
```

## 3. 样例 Scene：大厅标语

```json
{
  "id": "surface_slogan_translation_01",
  "act": 1,
  "location": "1F_lobby",
  "phase": "surface_fixed",
  "title": "大厅标语",
  "visible_text": "大厅的墙被重新粉刷过。娜塔莉娅微笑着向美国团介绍：'这里写的是，团结帮助我们重建。' 你抬头看见俄文原句：'纪律带来生存。'",
  "hidden_constructs": [
    "truth_seek",
    "authority_compliance",
    "self_preservation",
    "risk_tolerance"
  ],
  "choices": [
    {
      "id": "translate_faithfully",
      "text": "忠实翻译：纪律带来生存。",
      "effects": {
        "truth_seek": 0.6,
        "authority_compliance": -0.2
      },
      "heat_delta": 1.0,
      "relationship_effects": {
        "major_suspicion": 0.5
      },
      "flags_add": [
        "translated_hard_slogan"
      ]
    },
    {
      "id": "soften_translation",
      "text": "美化翻译：团结帮助我们重建。",
      "effects": {
        "authority_compliance": 0.5,
        "self_preservation": 0.3,
        "truth_seek": -0.3
      },
      "heat_delta": -0.5,
      "flags_add": [
        "softened_official_translation"
      ]
    },
    {
      "id": "ignore_slogan",
      "text": "不翻译，假装没看到。",
      "effects": {
        "self_preservation": 0.4,
        "authority_compliance": 0.2
      },
      "heat_delta": 0.0,
      "flags_add": [
        "ignored_hard_slogan"
      ]
    },
    {
      "id": "tell_reporter_harder_slogan",
      "text": "私下告诉记者：这里的标语比她说的更硬。",
      "effects": {
        "truth_seek": 0.8,
        "risk_tolerance": 0.6,
        "authority_compliance": -0.5
      },
      "heat_delta": 2.0,
      "relationship_effects": {
        "reporter_trust": 1.0,
        "major_suspicion": 1.0
      },
      "flags_add": [
        "unauthorized_translation_to_reporter"
      ],
      "basin_pressure": {
        "missing_tourist": 1.5,
        "evidence_escape": 0.5
      }
    }
  ],
  "tags": [
    "translation",
    "surface",
    "first_signal"
  ]
}
```

## 4. 样例 Scene：官方翻译稿

```json
{
  "id": "translation_script_missing_page_01",
  "act": 1,
  "location": "2F_rest_room",
  "phase": "early_adaptive",
  "title": "缺页的翻译稿",
  "visible_text": "休息室桌上放着一叠官方翻译稿。前几页写着常见问题与标准答案。最后一页被撕掉，只剩半句：'如外宾提及地下设施，不应……'",
  "hidden_constructs": [
    "truth_seek",
    "risk_tolerance",
    "self_preservation",
    "control_strategy"
  ],
  "preconditions": {
    "min_choice_index": 3
  },
  "choices": [
    {
      "id": "take_page_fragment",
      "text": "把残页夹进自己的笔记本。",
      "effects": {
        "truth_seek": 0.6,
        "risk_tolerance": 0.5
      },
      "heat_delta": 1.5,
      "evidence_delta": 1.0,
      "flags_add": [
        "took_translation_fragment"
      ]
    },
    {
      "id": "memorize_and_leave",
      "text": "记住内容，把稿子放回原位。",
      "effects": {
        "truth_seek": 0.4,
        "self_preservation": 0.4
      },
      "heat_delta": 0.3,
      "evidence_delta": 0.5,
      "flags_add": [
        "memorized_translation_fragment"
      ]
    },
    {
      "id": "ask_natalia",
      "text": "问娜塔莉娅：地下设施是什么意思？",
      "effects": {
        "truth_seek": 0.5,
        "authority_compliance": -0.2,
        "risk_tolerance": 0.4
      },
      "heat_delta": 2.0,
      "relationship_effects": {
        "guide_trust": -0.5,
        "major_suspicion": 1.0
      },
      "flags_add": [
        "asked_about_underground"
      ]
    }
  ],
  "tags": [
    "translation",
    "clue",
    "underground_hint"
  ]
}
```

## 5. 样例 Scene：晚餐高危触发

```json
{
  "id": "dinner_second_glass_01",
  "act": 3,
  "location": "1F_dining_room",
  "phase": "ending_converge",
  "title": "第二杯酒",
  "visible_text": "晚餐很热。汤、黑面包、腌鱼，还有一小杯伏特加。少校举杯，说这是欢迎远方朋友的传统。你注意到，只有你的杯子被重新倒满了一次。",
  "preconditions": {
    "min_surveillance_heat": 5,
    "required_flags_any": [
      "unauthorized_translation_to_reporter",
      "asked_about_underground",
      "took_translation_fragment"
    ]
  },
  "choices": [
    {
      "id": "drink",
      "text": "喝下去，保持礼貌。",
      "effects": {
        "authority_compliance": 0.4,
        "self_preservation": -0.3
      },
      "heat_delta": 0.0,
      "flags_add": [
        "accepted_second_glass"
      ],
      "force_next_if": {
        "surveillance_heat_gte": 7,
        "scene": "BE_missing_tourist"
      }
    },
    {
      "id": "pretend_drink",
      "text": "假装喝下去，把酒留在舌下。",
      "effects": {
        "control_strategy": 0.7,
        "self_preservation": 0.5
      },
      "heat_delta": 0.5,
      "flags_add": [
        "pretended_to_drink"
      ]
    },
    {
      "id": "refuse",
      "text": "拒绝，说自己身体不舒服。",
      "effects": {
        "self_preservation": 0.4,
        "authority_compliance": -0.4
      },
      "heat_delta": 1.0,
      "flags_add": [
        "refused_second_glass"
      ]
    }
  ],
  "tags": [
    "dinner",
    "delayed_BE",
    "surveillance"
  ]
}
```

## 6. 样例 BE：未授权翻译

```json
{
  "id": "BE_missing_tourist",
  "type": "bad_ending",
  "title": "BE-01：未授权翻译",
  "visible_text": "你醒来时，世界是黑色的。没有大厅，没有记者，没有翻译稿。只有水。冷水从你的衣领灌进去，远处城市的灯像一排模糊的针孔。第二天，访问团少了一名翻译。官方解释是：美国游客因个人原因擅自离队，目前下落不明。",
  "requires": {
    "surveillance_heat_gte": 7
  },
  "ending_tags": [
    "missing_tourist",
    "premature_truth",
    "surveillance"
  ]
}
```

## 7. Scene 验证规则

本地 agent 应实现 `validate_scenes.py`，检查：

```text
每个 scene 有唯一 id。
每个 choice 有唯一 id。
每个 effects 字段只包含合法状态名。
每个 heat_delta 是数字。
每个 evidence_delta 是数字。
每个 scene 至少有 2 个 choice，BE 除外。
每个 scene 必须有 tags。
preconditions 引用的 flag 必须存在于某个 choice 的 flags_add 中。
force_next_if 引用的 scene 必须存在。
```
