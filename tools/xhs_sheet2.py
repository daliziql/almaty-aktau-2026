#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gate-2 联系表：把 imgs2/<key>/<note>/img_xx.webp 拼成带编号的网格图，
供 MainAgent 逐张视觉核验。输出 raw/xhs/sheets2/<key>_pN.jpg + manifest.json。
编号规则：<note后6位>-<img序号>，manifest 记录编号→文件/标题/原帖。
"""
import os, json, glob
from PIL import Image, ImageDraw, ImageFont

TRIP="/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
SRC=os.path.join(TRIP,"raw/xhs/imgs2")
OUT=os.path.join(TRIP,"raw/xhs/sheets2"); os.makedirs(OUT,exist_ok=True)
COLS,PER=5,30
TW,TH=260,260; PAD=8; LH=30; HEAD=54
FONT=None
for fp in ["/System/Library/Fonts/PingFang.ttc","/System/Library/Fonts/Helvetica.ttc"]:
    if os.path.exists(fp):
        try: FONT=ImageFont.truetype(fp,17); break
        except: pass
FONTB=FONT

def load_notes(key):
    titles={}
    for nj in glob.glob(os.path.join(SRC,key,"*","note.json")):
        d=json.load(open(nj,encoding="utf-8")); titles[d["id"]]=d.get("title","")[:24]
    return titles

def build_key(key):
    titles=load_notes(key)
    items=[]
    for nd in sorted(glob.glob(os.path.join(SRC,key,"*"))):
        nid=os.path.basename(nd)
        for img in sorted(glob.glob(os.path.join(nd,"*.webp"))):
            code=f"{nid[-6:]}-{os.path.basename(img)[4:6]}"
            items.append({"code":code,"path":img,"nid":nid,"title":titles.get(nid,"")})
    manifest={}
    pages=[]
    for pi in range(0,len(items),PER):
        chunk=items[pi:pi+PER]; rows=(len(chunk)+COLS-1)//COLS
        W=COLS*(TW+PAD)+PAD; H=HEAD+rows*(TH+LH+PAD)+PAD
        canvas=Image.new("RGB",(W,H),(245,245,245))
        dr=ImageDraw.Draw(canvas)
        dr.text((PAD,14),f"{key}  p{pi//PER+1}  ({pi+1}-{pi+len(chunk)}/{len(items)})",fill=(20,20,20),font=FONTB)
        for j,it in enumerate(chunk):
            r,c=divmod(j,COLS); x=PAD+c*(TW+PAD); y=HEAD+r*(TH+LH+PAD)
            try:
                im=Image.open(it["path"]).convert("RGB"); im.thumbnail((TW,TH))
                canvas.paste(im,(x+(TW-im.width)//2,y+(TH-im.height)//2))
            except Exception as e:
                dr.rectangle([x,y,x+TW,y+TH],fill=(220,80,80)); dr.text((x+8,y+8),"BROKEN",fill="white",font=FONT)
            dr.rectangle([x,y+TH,x+TW,y+TH+LH],fill=(30,30,30))
            dr.text((x+6,y+TH+5),it["code"],fill="white",font=FONT)
            manifest[it["code"]]={"path":it["path"],"nid":it["nid"],"title":it["title"]}
        fp=os.path.join(OUT,f"{key}_p{pi//PER+1}.jpg")
        canvas.save(fp,quality=82); pages.append(fp)
    json.dump(manifest,open(os.path.join(OUT,f"{key}_manifest.json"),"w",encoding="utf-8"),ensure_ascii=False,indent=1)
    return pages,len(items)

if __name__=="__main__":
    import sys
    keys=sys.argv[1:] or sorted(os.listdir(SRC))
    grand=0
    for k in keys:
        if not os.path.isdir(os.path.join(SRC,k)): continue
        pages,n=build_key(k); grand+=n
        print(f"{k}: {n} imgs -> {len(pages)} sheet(s)")
    print("total",grand)
