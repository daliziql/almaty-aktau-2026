# 信息源清单（shared，持续登记）

> 每发现一个有用的内部群、文档或外部渠道就登记在这里，后续行程直接复用，不必重新摸索。
> 最近一次全量探查：2026-08-31（企业知识搜索 + lark-cli im +chat-search 实测）。

## 内部飞书群（旅游相关，均已实测可见）

| 群名 | chat_id | 群模式 | 价值点 |
|---|---|---|---|
| 旅游分享＆游玩攻略＆摄影作品＆约玩计划 | oc_ebd8b3054919a82cc9613f4938912286 | 话题群 | 攻略分享主群之一，同事自发攻略+开源 skill 多出自此 |
| 旅游分享＆游玩攻略＆摄影作品＆约玩计划（2） | oc_75e427ebeea68be7c7c90c191c236963 | 话题群 | 主群2群，组局/攻略/照片/资源分享 |
| 字节旅行交流群1️⃣-旅游/徒步/登山/滑雪/户外 | oc_da584d936064822640b27d84318124a4 | 话题群 | 老牌大群（2019 起），找搭子+互助攻略+旅行动态 |
| 字节旅行交流群3️⃣-旅游/徒步/登山/滑雪/户外 | oc_e3f0590ac17f721d14325ba4e9d62a3c | 话题群 | 新分群（2026-05），最新讨论在这里，注意是否还有2群待补查 |
| 字节旅行交流群【日本】 | oc_ef5dfcd4e46d4c6e5c2bb24cbd3bbe56 | 普通群 | 日本目的地专属，游玩组队+攻略共享 |
| 西藏旅行攻略交流 | oc_b1dbb59aa159b8711b6977aa958e329c | 普通群 | 西藏目的地专属 |

> 采集方式：话题群优先按话题（thread）拉取；`lark-cli im +chat-messages-list --chat-id <oc_xxx> --start/--end`，
> 跨群补漏用 `+messages-search --query <关键词>`。

## 内部核心文档（总表/索引级，优先读）

| 标题 | 链接 | 主题 | 备注 |
|---|---|---|---|
| 旅行目的地红黑榜（欢迎补充） | https://bytedance.larkoffice.com/sheets/TPo9sN4Kch8p2gtXhMicrfP4nme | 全球目的地红黑榜总表 | owner 曹宽怡；按城市打分+评价+攻略链接，**红黑经验第一信源**，持续更新（最近 2026-08-30） |
| 旅游群内攻略文档合集 | https://bytedance.larkoffice.com/docx/FnXNdrHSto2QFFxd7NAcK3kYn1f | 群内全部攻略文档索引 | owner 徐玥；按大洲/国家分类汇总攻略链接，找具体目的地攻略先查它 |
| 字节旅行组队 | https://bytedance.larkoffice.com/sheets/IqOKsQClehVu0ttTotKcOxSOnqc | 各假期组队表 | owner 张灿灿；可看目的地热度与同行人 |
| 2026 游玩攻略素材库与整合版 | https://bytedance.larkoffice.com/docx/NI3YdJnEao04MPxYpB1c0YgFnWt | 2026 明星路线卡片 | owner 方俊辉；路线适合人群+决策前必确认项 |
| 2026国庆出游去向总结 | https://bytedance.larkoffice.com/docx/LoxSdSPqoo5vSKxLnJ3cgYZQnNc | 群聊+组队表热度统计 | 口径说明清晰，可复用其统计方法 |

## 内部已有的目的地攻略样例（节选，全文索引见「文档合集」）

| 目的地 | 链接 | 亮点 |
|---|---|---|
| 印尼（泗水/布罗莫/伊珍/巴厘岛） | https://bytedance.larkoffice.com/docx/X31cdGbeHoJ8sSxgRc3cdfX4nVg | 火山线详细攻略 |
| 印尼（潜进印尼·2026国庆） | https://bytedance.larkoffice.com/docx/QH6wd6SBDomQHaxWkimc9Z16nfe | 船宿潜水 |
| 欧洲4国8城11天 | https://bytedance.larkoffice.com/docx/FfrmdX4hGo3upSx3X3nc47ZKnTh | 自由行 |
| 埃及 | https://bytedance.larkoffice.com/docx/KH9udUFiHohSL4xy12QcZ4v8nic | 含大量防骗黑榜 |
| 清迈（2026中秋国庆） | https://bytedance.larkoffice.com/docx/KqlUd0Aboo69PUx4T6LcMq7inxd | 避坑表格式可借鉴 |
| 云南滇西北—滇西环线 | https://bytedance.larkoffice.com/docx/Kx6fdXghOolKeexqhy9cKy0Fnec | 分地区避坑 |
| 北疆阿勒泰—禾木—喀纳斯 | https://bytedance.larkoffice.com/docx/DZF3dFtF0ouBn0xleVdcJI09nxd | 错峰线+保底方案 |

## 同事开源的同类工具（参考对标，迭代 shared 时借鉴）

- travel-planner skill（同事钟雨涵开源）：给机票+预算直接生成成稿攻略，强调真实链接校验、记忆偏好、排版。
  - AgentBuddy：https://skills.bytedance.net/skill/skills:skills.byted.org/default/public/travel-planner:1.0.0
  - GitHub：https://github.com/NealK6688/travel-planner-skill

## 本人历史方案文档（周启立，可复用前期调研）

- 2026 国庆 7 天旅行攻略对比（广州/上海双城出发）：https://bytedance.larkoffice.com/docx/JGZrduOqOo4peLxMtficenGWnac
- 2026 国庆 7 天三方案深度对比 v2（印尼东爪哇/Rinjani/中亚）：https://bytedance.larkoffice.com/docx/ZvKMdQqagoNRjCxi29AcerkZnCh
- 2026 国庆印尼 6-7 天攻略（双城出发版）：https://bytedance.larkoffice.com/docx/PUVqdtI7Toh99zxKinCc48FRnnd
- 2026 国庆印尼 7 天（Rinjani 徒步+Bali 躺平）：https://bytedance.larkoffice.com/docx/OsTfdFHxeow619xSHUkczyPXnqf

## 外部固定渠道（公开，按行程补充）

| 渠道 | 用途 | 链接 |
|---|---|---|
| 12306 / 航司官网 | 大交通票务与放票时间 | |
| 景区官方公众号/官网 | 预约、承载量、封闭公告（如喀纳斯、玉龙雪山小程序） | |
| 中央气象台/地方天气 | 天气与雨雪台风预警 | |

## 哈萨克斯坦/中亚专线（2026-10 行程沉淀，后续中亚行程复用）

| 渠道 | 用途 | 链接 |
|---|---|---|
| 中国驻哈使馆/驻阿拉木图总领馆 | 免签政策、入境材料、安全提醒 | https://kz.china-embassy.gov.cn/ ；https://almaty.china-consulate.gov.cn/ |
| 南航英文时刻表 PDF | CZ 中亚航线班期核验（如 CZ3084 ALA-CAN） | http://www.csair.com/en/bookings/flight_times/resource/hangbanshikebiaoyingwenxin.pdf |
| FlyArystan 官网航线页 | 哈国内陆廉航时刻（注意行李另购） | https://flyarystan.com/ |
| GetYourGuide / Redmaya / travel-mangystau.kz | 阿拉木图周边团、曼吉斯套 jeep 团报价与班期、营地温度口径 | 见各行程 raw/素材来源快照 |
| WeatherSpark / Weather Atlas | 目的地逐月份气温/降水分布 | https://zh.weatherspark.com/ |
| 打车 | 哈国统一用 Yandex Go，机场拉客出租溢价 5-10 倍（内部实测） | App |

## 登记规则

1. 内部群优先记录「群名 + chat_id + 群定位」，chat_id 从 `lark-cli im +chat-search` 获取。
2. 文档必须保留完整 URL（含 query/锚点），不得截断。
3. 标注信息时效；失效来源定期清理但保留一行「曾用 + 失效原因」。
4. 每次新行程结束，把新发现的好用来源回灌到本文件。
