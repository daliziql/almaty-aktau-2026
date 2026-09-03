#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""增量入库 imgs3 双 Gate 选出的 4 个新点位，压缩并合并 gallery-data.js / provenance.json"""
import json, os
from PIL import Image

ROOT = "/Users/bytedance/workspace/travel-books"
RAW = os.path.join(ROOT, "raw/xhs/imgs3")
GAL = os.path.join(ROOT, "assets/gallery2")

NOTES = {
 "6a68d318": ("阿拉木图两湖一峡谷攻略", "50"),
 "6a8031bf": ("一场不会后悔的两天两夜旅行", "10"),
 "6a93fc87": ("阿拉木图最后一程｜两湖一峡谷", "9"),
 "6a50c3fd": ("阿拉木图最惊艳的是游戏建模般的峡谷", "27"),
 "681c361f": ("阿拉木图两湖一峡谷旅行团最详细说明4/5", "32"),
 "6a81f418": ("两日一峡谷 day2 恰伦峡谷", "3"),
 "665dd07c": ("阿拉木图3D2N跟团游", "19"),
 "68f86e8a": ("灯塔楼——阿克套城标之一", "29"),
 "67e684d9": ("阿克套 Melovoy 屋顶灯塔", "7"),
 "6900e217": ("灯塔下的阿克套", "4"),
 "6a8db456": ("旅行日记｜阿克套city walk看建筑雕像篇", "25"),
 "69f6714c": ("阿克套小众博物馆，珍藏众多标本", "36"),
 "6852e341": ("哈萨克斯坦之行 阿克套变形计", "21"),
}
TITLES = {
 "black_canyon": "黑峡谷 Black Canyon",
 "moon_canyon": "月亮峡谷 Moon Canyon",
 "aktau_lighthouse": "阿克套 Melovoy 屋顶灯塔",
 "mangystau_museum": "曼吉斯套州立博物馆",
}
def src(nid, f):
    for base in [os.path.join(RAW,"black_canyon",nid), os.path.join(RAW,"moon_canyon",nid), os.path.join(RAW,"_pool",nid),
                 os.path.join(RAW,"_pool","lighthouse"), os.path.join(RAW,"_pool","cw_build"),
                 os.path.join(RAW,"_pool","museum_a"), os.path.join(RAW,"_pool","museum_d"),
                 os.path.join(RAW,"_pool","3d2n")]:
        p = os.path.join(base, f)
        if os.path.exists(p): return p
    raise FileNotFoundError(f"{nid}/{f}")

PLAN = {
 "black_canyon": [
   ("6a68d318","bc_01.jpg"),("6a68d318","bc_13.jpg"),("6a68d318","bc_14.jpg"),
   ("6a8031bf","p03.jpg"),("6a93fc87","q04.jpg"),("6a93fc87","q06.jpg"),
   ("6a50c3fd","j_06.jpg"),("6a50c3fd","j_07.jpg"),("6a50c3fd","j_08.jpg"),
   ("681c361f","w_03.jpg"),
 ],
 "moon_canyon": [
   ("6a8031bf","p04.jpg"),("6a81f418","s_00.jpg"),("681c361f","w_04.jpg"),
   ("665dd07c","y_07.jpg"),("665dd07c","y_09.jpg"),("665dd07c","y_12.jpg"),
 ],
 "aktau_lighthouse": [
   ("68f86e8a","la00.jpg"),("68f86e8a","la01.jpg"),
   ("67e684d9","lc00.jpg"),("67e684d9","lc01.jpg"),("67e684d9","lc02.jpg"),("67e684d9","lc03.jpg"),
   ("6900e217","ld00.jpg"),
   ("6a8db456","lf02.jpg"),("6a8db456","lf03.jpg"),("6a8db456","lf05.jpg"),
 ],
 "mangystau_museum": [
   ("69f6714c","ma00.jpg"),("69f6714c","ma01.jpg"),("69f6714c","ma02.jpg"),
   ("69f6714c","ma04.jpg"),("69f6714c","ma05.jpg"),("69f6714c","ma08.jpg"),
   ("6852e341","md00.jpg"),("6852e341","md01.jpg"),("6852e341","md03.jpg"),("6852e341","md05.jpg"),
 ],
}

def save_webp(s, out, edge, q):
    im = Image.open(s).convert("RGB")
    w,h = im.size
    if max(w,h) > edge:
        k = edge/max(w,h); im = im.resize((round(w*k),round(h*k)), Image.LANCZOS)
    im.save(out, "WEBP", quality=q, method=6)

new_js = {}
prov_add = []
for key, items in PLAN.items():
    d = os.path.join(GAL, key); os.makedirs(d, exist_ok=True)
    arr = []
    for i,(nid,f) in enumerate(items, 1):
        sp = src(nid,f)
        stem = f"{key}_{i:02d}"
        main = os.path.join(d, stem+".webp"); th = os.path.join(d, stem+".th.webp")
        save_webp(sp, main, 1280, 70); save_webp(sp, th, 480, 62)
        title, like = NOTES[nid]
        rel = f"assets/gallery2/{key}/{stem}.webp"
        url = f"https://www.xiaohongshu.com/explore/{nid}"
        arr.append({"src": rel, "cap": title, "url": url, "like": like})
        prov_add.append({"code": f"{nid[-6:]}-{f.split('.')[0]}", "file": rel, "like": like,
                         "note_id": nid, "title": title, "url": url})
    new_js[key] = {"title": TITLES[key], "items": arr}
    print(key, len(arr))

js_path = os.path.join(GAL,"gallery-data.js")
txt = open(js_path, encoding="utf-8").read()
assert "window.GALLERY={" in txt
blocks = []
for key,obj in new_js.items():
    lines = [f'  "{key}": {{title:"{obj["title"]}", items:[']
    for it in obj["items"]:
        lines.append('    {"src": "%s", "cap": "%s", "url": "%s", "like": "%s"},' % (it["src"],it["cap"],it["url"],it["like"]))
    lines[-1] = lines[-1][:-1]
    lines.append("  ]},")
    blocks.append("\n".join(lines))
insert = "\n" + "\n".join(blocks) + "\n"
idx = txt.rstrip().rfind("}")
txt2 = txt[:idx] + insert + txt[idx:]
open(js_path,"w",encoding="utf-8").write(txt2)

pv = os.path.join(GAL,"provenance.json")
prov = json.load(open(pv, encoding="utf-8"))
prov["black_canyon"] = prov_add[0:10]
prov["moon_canyon"] = prov_add[10:16]
prov["aktau_lighthouse"] = prov_add[16:26]
prov["mangystau_museum"] = prov_add[26:36]
json.dump(prov, open(pv,"w",encoding="utf-8"), ensure_ascii=False, indent=2)
print("done")
