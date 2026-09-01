#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate-2 成品构建 v2：
- 读 gate2_select.json + sheets2 manifest，把精选图复制到 assets/gallery2/<entity>/
- provenance.json：图→原笔记溯源
- gallery-data.js：window.GALLERY（旧 schema {title,items:[{src,cap,url,like}]}），
  既暴露 38 个实体键，也按 HTML_MAP 暴露 HTML 里使用的聚合/旧键。
"""
import os,json,shutil
TRIP="/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
TOOLS="/Users/bytedance/workspace/travel-books/tools"
SRC=os.path.join(TRIP,"raw/xhs/imgs2"); SHEETS=os.path.join(TRIP,"raw/xhs/sheets2")
DST=os.path.join(TRIP,"assets/gallery2")
sel=json.load(open(os.path.join(TOOLS,"gate2_select.json"),encoding="utf-8"))

ZH={"cathedral":"升天大教堂","memorial_park":"潘菲洛夫28勇士公园","museum_csm":"中央国家博物馆",
"abay_opera":"阿拜歌剧院","metro":"阿拉木图地铁","green_bazaar":"绿巴扎","barakholka":"Barakholka旧货市场",
"koktobe":"Kok Tobe 科克托别山","central_mosque":"中央清真寺","arbat":"Arbat 步行街","brutalism":"苏式粗野主义建筑",
"atelier_bar":"Atelier 调酒酒吧","bao_lake":"大阿拉木图湖 BAO","bao_pipe":"BAO 管道徒步","glacier":"博格达诺维奇冰川",
"shymbulak":"琼布拉克 Shymbulak","medeu":"Medeu 麦迪奥","kolsai":"科尔赛湖 Kolsai","kaindy":"卡因迪湖 Kaindy",
"charyn":"恰伦峡谷 Charyn","issyk":"耶斯克湖 Issyk","turgen":"Turgen 吐尔根","assy":"Assy 高原天文台",
"kokzhailau":"Kok-Zhailau 高原","torysh":"Torysh 球谷","sherkala":"Sherkala 狮山·Ayrakty",
"shakpakata":"Shakpak-Ata 地下清真寺","kyzylkup":"Kyzylkup 提拉米苏彩丘","bozzhyra":"Bozzhyra 尖牙群",
"bokty":"Bokty 堡垒山","zhygylgan":"Zhygylgan 坍塌盆地","tuzbair":"Tuzbair 粉色盐沼","aktau_city":"阿克套市区·里海",
"navat":"Navat 餐厅","auyl":"Auyl 餐厅","smile":"Shashlychok 红房子烤肉","hosejosper":"Xose&Josper 牛排","aroma":"Aroma 早午餐",
"daredzhani":"Daredzhani 格鲁吉亚菜","saty_village":"Saty 村民宿与哈萨克家宴","uaz_kaindy":"卡因迪 UAZ 越野搓板路",
"arasan_banya":"Arasan 苏式浴馆","sandyq":"Sandyq 国宴民族菜","airakty":"Airakty-Shomanai 城堡谷",
"karynzharyk":"Karynzharyk 洼地","beket_ata":"Beket-Ata 地下清真寺","chechil_pub":"CHECHIL PUB 海边牛扒"}

# HTML 旧键/聚合键 → 实体列表
HTML_MAP={
 "citywalk_cathedral":["cathedral"],"citywalk_memorial":["memorial_park"],"citywalk_mosque":["central_mosque"],
 "citywalk_metro":["metro"],"citywalk_brutalism":["brutalism"],"citywalk_street":["arbat"],
 "green_bazaar":["green_bazaar"],"barakholka_flea":["barakholka"],"koktobe":["koktobe"],"museum":["museum_csm"],
 "abay_opera":["abay_opera"],"atelier_bar":["atelier_bar"],
 "bao_pipe":["bao_pipe"],"glacier":["glacier"],"charyn":["charyn"],
 "kolsai":["kolsai"],"kaindy":["kaindy"],"kolsai_kaindy":["kolsai","kaindy"],
 "aktau_city":["aktau_city"],"alt_kyzylkup":["kyzylkup"],"alt_bozzhyra":["bozzhyra","bokty"],
 "alt_shakpak_ata":["shakpakata"],"tuzbair":["tuzbair"],
 "food_smile":["smile"],"food_navat":["navat"],"food_hosejosper":["hosejosper"],"food_auyl":["auyl"],
 "food_local":["aroma"],
 "torysh":["torysh"],"sherkala":["sherkala"],"kyzylkup":["kyzylkup"],"bozzhyra":["bozzhyra"],"bokty":["bokty"],
 "shymbulak":["shymbulak"],"medeu":["medeu"],
}

def note_meta(key,nid):
    p=os.path.join(SRC,key,nid,"note.json")
    if os.path.exists(p):
        d=json.load(open(p,encoding="utf-8"))
        return d.get("title",""),d.get("url",""),d.get("like","")
    return "","",""

if os.path.exists(DST): shutil.rmtree(DST)
os.makedirs(DST,exist_ok=True)
entity_items={}; prov={}
for key,codes in sel.items():
    man=json.load(open(os.path.join(SHEETS,f"{key}_manifest.json"),encoding="utf-8"))
    od=os.path.join(DST,key); os.makedirs(od,exist_ok=True)
    entity_items[key]=[]; prov[key]=[]; n=0
    for code in codes:
        if code not in man: print("!! missing",key,code); continue
        nid=man[code]["nid"]; n+=1
        fn=f"{key}_{n:02d}.webp"; shutil.copy(man[code]["path"],os.path.join(od,fn))
        title,url,like=note_meta(key,nid)
        rel=f"assets/gallery2/{key}/{fn}"
        entity_items[key].append({"src":rel,"cap":title,"url":url,"like":like})
        prov[key].append({"file":rel,"code":code,"note_id":nid,"title":title,"url":url,"like":like})
json.dump(prov,open(os.path.join(DST,"provenance.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)

galleries=dict(entity_items)
titles=dict(ZH)
for hk,ents in HTML_MAP.items():
    it=[]
    for e in ents: it+=entity_items[e]
    galleries[hk]=it
    titles[hk]=" + ".join(ZH[e] for e in ents)

out=["/* AUTO-BUILT gallery2 · 图片均来自小红书笔记，登录态模拟人工浏览+逐张AI核验，版权归原作者，仅个人行程参考 */","window.GALLERY={"]
for k,items in galleries.items():
    out.append(f"  {json.dumps(k,ensure_ascii=False)}: {{title:{json.dumps(titles.get(k,k),ensure_ascii=False)}, items:[")
    for it in items:
        out.append("    "+json.dumps(it,ensure_ascii=False)+",")
    out.append("  ]},")
out.append("};")
open(os.path.join(DST,"gallery-data.js"),"w",encoding="utf-8").write("\n".join(out))
tot=sum(len(v) for v in entity_items.values())
print("entities",len(entity_items),"imgs",tot,"html keys",len(galleries))
for k,v in entity_items.items(): print(k,len(v))
