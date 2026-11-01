# CINDER RELAY — Story Bible

## 已批准的故事事实

| 项目 | 事实 |
| --- | --- |
| 主角 | Elias Venn |
| 性别／年龄 | 男性，28 岁 |
| 职业 | 机械维修技师 |
| 故事年代 | 2118 年 |
| 历史转折 | The Quieting：数十年前全球基础设施发生灾难性停摆 |
| 叙事主线 | 恢复废弃设施，重新发现技术，揭开 MERIDIAN 网络的真相 |
| 第一章 | Chapter 01 — The Dead Station |
| 第一章场景 | 废弃铁路场 → 维修工坊 → 地下中继站（顺序为规划默认，具体剧本待定） |

## 叙事实施原则

维修师身份应体现在玩家观察故障、回收材料、修复设备与使用工具的行为中。优先通过场景、声音、动画和短段交互传达信息；长过场是否需要另行决定。这是制作建议，不增写人物背景或剧情事实。

第一章应表达一个可以理解的局部目标，在结尾给出阶段性完成感和关于 MERIDIAN 的可辨认线索。线索内容、真假及后续解释尚未批准。使用内部工作标记时必须写“待定”，不能把占位文本当作最终台词。

## 不得擅自填补的空白

- The Quieting 的确切年份、原因、责任方和伤亡范围。
- MERIDIAN 的性质、目的、当前控制者、是否具有意识或善恶立场。
- Elias 的亲属、所属组织、创伤、个人秘密、外貌及配音。
- 后续敌人／阵营及事件顺序。Phase02 已批准本章铁路场遭遇人形 Ash Warden 侦察兵，正在搜索废弃铁路设备；不得据此扩写阵营历史、政治或与 MERIDIAN 的关系。
- 主角恢复设施的动机、秘密行动是否保留、最终结局与道德选择。

本文件与用户后续批准的剧情共同构成 canon。每次重大剧情决定在决策日志中注明来源；引用外部作品仅用于分析，不复制其角色、对白、音乐或美术。

## Phase03 provisional subtitles — not new canon

These temporary English lines are inspectable in CRPlayerController/CRWorkbench. They do not define The Quieting's cause, MERIDIAN's nature or a radio operator's identity. No recorded voice or external audio is used.

| Session flag | Trigger | Temporary subtitle |
| --- | --- | --- |
| CR03_WorkshopDiscovery | First objective advance to FindModule | ELIAS: A calibration bench. I can still put this place to use. |
| CR03_AssemblyReflection | First actual presentation crossing4s | ELIAS: Funny. Machines remember what people forget. |
| CR03_RelayEcho | Original relay advances to InvestigateSignal | [A broken carrier tone returns.] ELIAS: Something on the other end is still listening. |

Flags live in the chapter GameMode and suppress replay after streamed-area returns. A reflection already heard before cancellation stays heard until Restart. Subtitles use the existing HUD, remain understandable without voice acting and clear after a bounded game-time duration. The final text remains exactly `MERIDIAN NETWORK` / `CONNECTION RESTORED`.
# Phase05 provisional environmental writing

No additional canon is established. The cause of The Quieting and MERIDIAN's motives remain unknown. The following temporary English presentation lines/records await narrative approval:

- Opening: "THE DEAD STATION / 2118" and Elias: "Workshop lights. There may be a way to bring the relay back."
- Workshop record: "MAINTENANCE / OPEN WORK ORDER — Relay Nine: power unit removed. Return replacement to access terminal."
- Bunker record: "LOCAL CONTROL / RELAY NINE — CARRIER TEST INCOMPLETE — Awaiting acknowledgement."
- Ending subtitle: "RELAY NINE / LOCAL POWER STABLE" and "[The returned signal breaks into an irregular carrier tone.]"

Existing Phase03 discovery/reflection/echo lines retain their existing stable session flags. New wall records and the opening/ending presentation do not add IDs to schema1. Restoration settles the relay's steady light from the existing objective without replaying an old sequence. There is no new radio operator, voice performance or confirmed explanation of the catastrophe. The final on-screen text remains MERIDIAN NETWORK / CONNECTION RESTORED.
