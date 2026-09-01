# -*- coding: utf-8 -*-
import io
p="/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套/行程攻略.html"
s=io.open(p,encoding="utf-8").read()
R=[]
def rep(old,new,tag):
    global s
    assert s.count(old)==1, f"[{tag}] count={s.count(old)}"
    s=s.replace(old,new); R.append(tag)

# 1) D2 行程1（打车去旧货市场）去掉与行程2重复的图集
rep("['drive','09:15','打车去 Barakholka 旧货大巴扎（城北 Severnoe Koltso，近机场）','旧货区仅周六日开，9 点出摊、部分摊 13-15 点收，赶早','barakholka_flea']",
    "['drive','09:15','打车去 Barakholka 旧货大巴扎（城北 Severnoe Koltso，近机场）','旧货区仅周六日开，9 点出摊、部分摊 13-15 点收，赶早']",
    "D2-去重Barakholka")

# 2) D4 晚餐 Navat → Daredzhani 格鲁吉亚菜（消除与 D1 重复）
rep("['food','19:30','Navat 国菜 + 采购早餐包','次日 03:30 起床，早睡','food_navat']",
    "['food','19:30','Daredzhani 格鲁吉亚菜 + 采购早餐包','换个口味：奶酪烤饼/蘑菇炖鸡；次日 03:30 起床，早睡','daredzhani']",
    "D4-Navat换Daredzhani")

# 3) D6 Bozzhyra 日落（与行程4同点）去重，不挂重复图集
rep("['hike','18:15','⭐ Bozzhyra 日落（全程最出片 45 分钟）','白垩崖从雪白染金粉，留给三脚架','bozzhyra']",
    "['hike','18:15','⭐ Bozzhyra 日落（全程最出片 45 分钟）','白垩崖从雪白染金粉，留给三脚架；实拍见上一条同点图集']",
    "D6-日落去重")

# 4) D7 管道/大湖拆成专属图集
rep("['hike','15:45','大阿拉木图湖（2511m）','Tiffany 蓝，拍摄 45 分钟，严禁下水','bao_pipe']",
    "['hike','15:45','大阿拉木图湖（2511m）','Tiffany 蓝，拍摄 45 分钟，严禁下水','bao_lake']",
    "D7-大湖专属图")

# 5) D8 07:45 到 Shymbulak 挂缆车专属图
rep("['drive','07:45','冰川团向导接，08:30 到 Shymbulak','三段缆车直上 3200m']",
    "['drive','07:45','冰川团向导接，08:30 到 Shymbulak','三段缆车直上 3200m','shymbulak']",
    "D8-Shymbulak缆车")

# 6) D7 晚有余兴 Kok Tobe 挂夜景图
rep("['food','19:15','晚餐+拉伸，备明早冰川装备','分层衣/手套/帽子/墨镜/热水；有余兴 21:00 可上 Kok Tobe 补夜景（缆车运营到 24:00，往返 1700 坚戈）']",
    "['food','19:15','晚餐+拉伸，备明早冰川装备','分层衣/手套/帽子/墨镜/热水；有余兴 21:00 可上 Kok Tobe 补夜景（缆车运营到 24:00，往返 1700 坚戈）','koktobe']",
    "D7-KokTobe夜景")

# 7) D5 Bomba 晚餐挂专属图
rep("['food','19:00','Bomba 正对里海日落晚餐','营业到凌晨 1 点']",
    "['food','19:00','Bomba 正对里海日落晚餐','营业到凌晨 1 点','bomba_aktau']",
    "D5-Bomba")

# 8) D3 Saty 村民宿家宴
rep("['stay','18:00','Saty 村民宿 + 19:00 哈萨克家宴','手抓肉/奶茶/包尔萨克']",
    "['stay','18:00','Saty 村民宿 + 19:00 哈萨克家宴','手抓肉/奶茶/包尔萨克','saty_village']",
    "D3-Saty村民宿")

# 9) D4 UAZ 越野进卡因迪
rep("['drive','08:30','从 Saty 村民宿出发，UAZ 越野进卡因迪','搓板路约 30km/1h，必须越野车（不回阿拉木图）']",
    "['drive','08:30','从 Saty 村民宿出发，UAZ 越野进卡因迪','搓板路约 30km/1h，必须越野车（不回阿拉木图）','uaz_kaindy']",
    "D4-UAZ越野")

# 10) 徒步专栏：管道与大湖按钮分开
rep('<h4>BAO 分步实操（评论区共识）<button class="g-btn" data-gal="bao_pipe">管道+大湖实拍 20</button></h4>',
    '<h4>BAO 分步实操（评论区共识）<button class="g-btn" data-gal="bao_pipe">管道实拍 10</button><button class="g-btn" data-gal="bao_lake">大湖实拍 10</button></h4>',
    "徒步专栏-管道/大湖拆分")

# 11) 备选：已有实体补按钮
rep('<b>Issyk 耶斯克湖（伊塞克湖，非吉尔吉斯那个）</b>：70km/1h15，海拔 1760m 滑坡堰塞湖，颜色从蒂芙尼蓝到深蓝；半日往返。<span class="m">可与 Turgen 熊瀑布连线一日，小团 $25-40/人</span>',
    '<b>Issyk 耶斯克湖（伊塞克湖，非吉尔吉斯那个）</b>：70km/1h15，海拔 1760m 滑坡堰塞湖，颜色从蒂芙尼蓝到深蓝；半日往返。<span class="m">可与 Turgen 熊瀑布连线一日，小团 $25-40/人</span><button class="g-btn" data-gal="issyk">实拍</button>',
    "备选-Issyk")
rep('<div class="alt-item"><b>Turgen 图尔根峡谷·熊瀑布</b>：70km/1.5h，松林徒步 1.5km/30min 到瀑布，顺路鳟鱼农场午餐，5-10 月最佳。</div>',
    '<div class="alt-item"><b>Turgen 图尔根峡谷·熊瀑布</b>：70km/1.5h，松林徒步 1.5km/30min 到瀑布，顺路鳟鱼农场午餐，5-10 月最佳。<button class="g-btn" data-gal="turgen">实拍</button></div>',
    "备选-Turgen")
rep('<div class="alt-item"><b>Assy 阿西高原</b>：150km/2.5-3h，2700m 牧场、毡房与马群；雨后土路难行必须 SUV，与 Issyk+Turgen 串成约 12h 大环线。</div>',
    '<div class="alt-item"><b>Assy 阿西高原</b>：150km/2.5-3h，2700m 牧场、毡房与马群；雨后土路难行必须 SUV，与 Issyk+Turgen 串成约 12h 大环线。<button class="g-btn" data-gal="assy">实拍</button></div>',
    "备选-Assy")
rep('<div class="alt-item"><b>Kok Zhailau 草甸徒步</b>：城市后山环线 3-4h，想加野趣可替换 D2 一个博物馆。</div>',
    '<div class="alt-item"><b>Kok Zhailau 草甸徒步</b>：城市后山环线 3-4h，想加野趣可替换 D2 一个博物馆。<button class="g-btn" data-gal="kokzhailau">实拍</button></div>',
    "备选-KokZhailau")
rep('<div class="alt-item"><b>Medeu 梅杰乌高山冰场</b>：市区 13km，与 D8 冰川同向；全球海拔最高的露天冰场之一，不滑冰也值得看大坝；可与 Shymbulak 缆车拼半天。<span class="m">交通：打车 20-25min；缆车约 09:00-22:00</span></div>',
    '<div class="alt-item"><b>Medeu 梅杰乌高山冰场</b>：市区 13km，与 D8 冰川同向；全球海拔最高的露天冰场之一，不滑冰也值得看大坝；可与 Shymbulak 缆车拼半天。<span class="m">交通：打车 20-25min；缆车约 09:00-22:00</span><button class="g-btn" data-gal="medeu">实拍</button></div>',
    "备选-Medeu")
rep('<div class="alt-item"><b>Arasan 浴馆</b>：市区苏式大澡堂，两湖/荒漠长途回来那晚泡 1.5h 回血。</div>',
    '<div class="alt-item"><b>Arasan 浴馆</b>：市区苏式大澡堂，两湖/荒漠长途回来那晚泡 1.5h 回血。<button class="g-btn" data-gal="arasan_banya">实拍</button></div>',
    "备选-Arasan")
rep('<div class="alt-item"><b>Sandyq</b>（Abylai Khan 55，12:00 开）：网红民族菜，环境比 Navat 更出片，需订位。</div>',
    '<div class="alt-item"><b>Sandyq</b>（Abylai Khan 55，12:00 开）：网红民族菜，环境比 Navat 更出片，需订位。<button class="g-btn" data-gal="sandyq">实拍</button></div>',
    "备选-Sandyq")
rep('<div class="alt-item"><b>Barbolsyn</b>（Valikhanova 47，与 Atelier 同址）：餐酒馆，人均 4000-10000 坚戈，D2 微醺第二摊。</div>',
    '<div class="alt-item"><b>Barbolsyn</b>（Valikhanova 47，与 Atelier 同址）：餐酒馆，人均 4000-10000 坚戈，D2 微醺第二摊。<button class="g-btn" data-gal="barbolsyn">实拍</button></div>',
    "备选-Barbolsyn")
rep('<div class="alt-item"><b>Aroma</b>：公认最佳 brunch，无花果 toast，小院出片；只收现金。</div>',
    '<div class="alt-item"><b>Aroma</b>：公认最佳 brunch，无花果 toast，小院出片；只收现金。<button class="g-btn" data-gal="food_local">实拍</button></div>',
    "备选-Aroma")

# 曼吉斯套备选按钮
rep('<div class="alt-item"><b>Zhygylgan「坠落之地」</b>：Tupkaragan 半岛，坍塌古海床巨盆+1.5km 临海悬崖步道与海蚀洞，和 Shakpak-Ata 同一条北线。</div>',
    '<div class="alt-item"><b>Zhygylgan「坠落之地」</b>：Tupkaragan 半岛，坍塌古海床巨盆+1.5km 临海悬崖步道与海蚀洞，和 Shakpak-Ata 同一条北线。<button class="g-btn" data-gal="zhygylgan">实拍</button></div>',
    "备选-Zhygylgan")
rep('<div class="alt-item"><b>Kapamsay 白垩峡谷</b>：距城约 130km，70m 高古河床白崖，北线延伸点。</div>',
    '<div class="alt-item"><b>Kapamsay 白垩峡谷</b>：距城约 130km，70m 高古河床白崖，北线延伸点。<button class="g-btn" data-gal="kapamsay">实拍</button></div>',
    "备选-Kapamsay")
rep('<div class="alt-item"><b>Airakty-Shomanai「城堡谷」</b>：4000 万年古海床蚀成的岩塔群，北线可替代或加塞球谷。</div>',
    '<div class="alt-item"><b>Airakty-Shomanai「城堡谷」</b>：4000 万年古海床蚀成的岩塔群，北线可替代或加塞球谷。<button class="g-btn" data-gal="airakty">实拍</button></div>',
    "备选-Airakty")
rep('<div class="alt-item"><b>Tamshaly 泉洲</b>：约 130km，崖壁渗下的淡水泉在荒漠里养出一小片绿洲，适合短徒步野餐。</div>',
    '<div class="alt-item"><b>Tamshaly 泉洲</b>：约 130km，崖壁渗下的淡水泉在荒漠里养出一小片绿洲，适合短徒步野餐。<button class="g-btn" data-gal="tamshaly">实拍</button></div>',
    "备选-Tamshaly")
rep('<div class="alt-item"><b>Karynzharyk 洼地+Kenderli 盐滩</b>：最低处低于海平面 75m，日出日落露营大片，深入 Ustyurt。</div>',
    '<div class="alt-item"><b>Karynzharyk 洼地+Kenderli 盐滩</b>：最低处低于海平面 75m，日出日落露营大片，深入 Ustyurt。<button class="g-btn" data-gal="karynzharyk">实拍</button></div>',
    "备选-Karynzharyk")
rep('<div class="alt-item"><b>Beket-Ata 地下清真寺</b>：哈萨克朝圣圣地，单日往返 600km+，只建议多住一天或有信仰目的再去，着装严格。</div>',
    '<div class="alt-item"><b>Beket-Ata 地下清真寺</b>：哈萨克朝圣圣地，单日往返 600km+，只建议多住一天或有信仰目的再去，着装严格。<button class="g-btn" data-gal="beket_ata">实拍</button></div>',
    "备选-BeketAta")
rep('<div class="alt-item"><b>Aydyn</b>：落地第一顿选它，鱼别尔卜克（fishbarmak）和鲟鱼汤，里海鱼比阿拉木图便宜。</div>',
    '<div class="alt-item"><b>Aydyn</b>：落地第一顿选它，鱼别尔卜克（fishbarmak）和鲟鱼汤，里海鱼比阿拉木图便宜。<button class="g-btn" data-gal="aydyn">实拍</button></div>',
    "备选-Aydyn")
rep('<div class="alt-item"><b>Krasny Mayak 红灯塔悬崖咖啡</b>：渔民棚屋改的野路子海景咖啡，包尔萨克+驼奶 shubat。</div>',
    '<div class="alt-item"><b>Krasny Mayak 红灯塔悬崖咖啡</b>：渔民棚屋改的野路子海景咖啡，包尔萨克+驼奶 shubat。<button class="g-btn" data-gal="krasny_mayak">实拍</button></div>',
    "备选-KrasnyMayak")

# 12) 餐饮卡：Bomba 加按钮、新增 Daredzhani 卡
rep('<div class="food"><span class="price">¥80-140</span><b>Bomba</b><div class="city">阿克套 · 到凌晨 1 点</div>面朝里海的日落海景位，D5 晚餐主场</div>',
    '<div class="food"><span class="price">¥80-140</span><b>Bomba</b><div class="city">阿克套 · 到凌晨 1 点</div>面朝里海的日落海景位，D5 晚餐主场<button class="g-btn" data-gal="bomba_aktau">实拍</button></div>',
    "餐饮-Bomba按钮")
rep('<div class="food"><b>其他本地小馆合集</b><div class="city">阿拉木图</div>穷游小馆、brunch、山景餐厅等实拍，吃腻连锁时翻牌子<button class="g-btn" data-gal="food_local">实拍合集</button></div>',
    '<div class="food"><b>其他本地小馆合集</b><div class="city">阿拉木图</div>穷游小馆、brunch、山景餐厅等实拍，吃腻连锁时翻牌子<button class="g-btn" data-gal="food_local">实拍合集</button></div>\n    <div class="food"><span class="price">¥60-100</span><b>Daredzhani</b><div class="city">阿拉木图 · 连锁</div>格鲁吉亚菜兜底：奶酪烤饼 Khachapuri、蘑菇炖鸡，D4 晚餐主场<button class="g-btn" data-gal="daredzhani">实拍</button></div>',
    "餐饮-Daredzhani卡")

io.open(p,"w",encoding="utf-8").write(s)
print("ALL EDITS OK:",len(R)); [print(" -",x) for x in R]
