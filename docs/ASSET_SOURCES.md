# CINDER RELAY — Asset Sources and Licensing

Phase 00 不下载大型第三方资源包、不购买资产，也不将本机引擎复制进仓库。新游戏素材导入前必须登记来源、作者、license、署名和再分发限制。

## 当前来源登记

| ID／内容 | 来源／作者 | 许可与署名 | 再分发限制 | 兼容与证据 |
| --- | --- | --- | --- | --- |
| EPIC-001：生成的 Blank C++ skeleton 与 template 配置 | Epic Games；本机 UE 5.8.4 `Templates/TP_Blank`，由官方 Editor 创建项目；[官方项目创建说明](https://dev.epicgames.com/documentation/en-us/unreal-engine/creating-a-new-project-in-unreal-engine) | [Unreal Engine EULA](https://www.unrealengine.com/en-US/eula/unreal)；保留原文件 Epic 版权注记；最终 credits 按适用条款审阅 | 不把引擎／Starter Content 原始库上传；生成内容与引用资源按各自适用条款处理，不标为 MIT／CC0 | 在 5.8.4 生成，CinderRelayEditor UBT baseline 有成功记录；打包／shipping 未验 |

当前没有外部 Fab 模型、动画、纹理、声音或 raw pack 入库。`/Engine/` 中被模板引用的内容属于引擎安装依赖，不代表已复制到本仓库或许可可独立再分发。通过 Editor 创建的项目自有地图单独记录生成方式；原始地图中的 Engine asset 引用仍需在最终包审核。

## Phase 01A 来源补充

| ID／内容 | 来源／作者 | 许可／署名／再分发 | 兼容与证据 |
| --- | --- | --- | --- |
| EPIC-002：Cube、Cylinder、默认 TextRender 字体／材质 | 本机官方 UE 5.8.4 `/Engine/BasicShapes` 与引擎默认 TextRender 依赖；Epic Games；[Epic Engine Content](https://dev.epicgames.com/documentation/en-us/unreal-engine/working-with-content-in-unreal-engine) | 适用 Unreal Engine EULA；保留 Epic 署名义务；只引用安装依赖，不复制引擎资源库或独立再分发素材 | 由真实 Editor 用于灰盒；未验证 packaged cook |
| CR-GEN-001：灰盒 map、8 个纯色材质、11 个输入资产、5 个配置 Blueprint | 本项目 `CinderRelay/Scripts/generate_greybox.py`；由本项目制作流程生成 | 项目自有编排，依赖部分仍遵循 Epic 条款；没有附加第三方素材 license 或对外开源许可 | UE 5.8.4 Editor 实际生成／保存，155 个具名对象；运行证据见 MILESTONES |

Phase 01A 未下载／购买外部资源，无 marketplace 运行依赖。所有 `.uasset`／`.umap` 使用现有 Git LFS；截图与原始运行日志保存在忽略目录。生成资产的精确内容 hash 由 Git LFS pointer 记录。

## 今后的必填记录

每个包记录：资产 ID／本地路径、source URL、作者／提供者、版本和获取日期、原文件 SHA256、完整 license 名称／版本／条款 URL、署名文本／位置、修改记录、redistribution 限制、允许的 repo 可见性、宣称引擎兼容、实际 UE 5.8.4 import／cook／runtime 证据、负责人和状态。

状态：candidate → license-cleared → import-tested → accepted，或 rejected。许可合规不能替代技术兼容，导入成功不能替代使用权。未知许可不下载／不导入；免费与可搜索到不等于可商用。

## 准入与仓库政策

1. 优先原作者／官方发行渠道，验证来源链。禁止游戏拆包、搬运站或无许可 copyrighted 内容。
2. 查骨架、比例／坐标轴、LOD、碰撞、材质、纹理预算、音频格式与插件版本。仅导入当前里程碑需要的资产，隔离每个外部包的目录。
3. 许可与收据存入合适的受控位置；不提交个人／支付信息或账户授权文件。私人 GitHub 也不是无限再分发许可。
4. 不将不必要的 raw asset packs、安装包、模型训练数据或整套第三方库存入 GitHub。必要二进制用 LFS；LFS 不能绕开版权条款。
5. 发布前核验实际 cooked 内容、credits 和 source distribution 范围；未经审查不切换公开仓库。

[Fab 官方许可摘要](https://www.fab.com/eula) 区分 Standard、CC-BY 等。Standard 允许在项目中整合使用，但禁止 standalone 资源再分发；每件商品仍需核对取得时的完整条款与访问级别。不要将某件资产的许可套用到另一件。

Codex 可整理公开证据、文件 hash、依赖和 cook 日志；许可歧义、购买／授权以及实际动画、材质与审美适用性需要相应人工审查。没有证据就标未验证。
