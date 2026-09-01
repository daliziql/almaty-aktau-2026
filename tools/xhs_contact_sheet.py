#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""为每篇小红书笔记生成带编号的联系表（contact sheet），用于逐张人工核验。"""
import os, json, math
from PIL import Image, ImageDraw, ImageFont

TRIP_DIR = "/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
IMG_ROOT = os.path.join(TRIP_DIR, "raw/xhs/imgs")
OUT = os.path.join(TRIP_DIR, "raw/xhs/contact_sheets")
META = os.path.join(TRIP_DIR, "raw/xhs/notes_read.jsonl")

TILE_W, TILE_H = 360, 420   # 单格尺寸（含标签条）
COLS = 4
LABEL_H = 34

def font(sz=20):
    for p in ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Helvetica.ttc"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, sz)
    return ImageFont.load_default()

def title_map():
    m = {}
    for line in open(META, encoding="utf-8"):
        d = json.loads(line)
        m[d["id"]] = (d.get("kw", ""), d["title"][:28])
    return m

def build_one(nid, tm):
    ddir = os.path.join(IMG_ROOT, nid)
    files = sorted(f for f in os.listdir(ddir) if f.endswith(".webp"))
    if not files: return None
    rows = math.ceil(len(files)/COLS)
    head = 56
    W = COLS*TILE_W
    H = head + rows*TILE_H
    sheet = Image.new("RGB", (W, H), "white")
    dr = ImageDraw.Draw(sheet)
    f0, f1 = font(22), font(19)
    kw, ti = tm.get(nid, ("", ""))
    dr.text((10, 8), f"{nid}  [{kw}]  {ti}", fill="black", font=f0)
    dr.text((10, 34), f"共 {len(files)} 张（编号即 img_xx）", fill=(120,120,120), font=f1)
    for i, fn in enumerate(files):
        r, c = divmod(i, COLS)
        x, y = c*TILE_W, head+r*TILE_H
        try:
            im = Image.open(os.path.join(ddir, fn)).convert("RGB")
        except Exception as e:
            continue
        im.thumbnail((TILE_W-8, TILE_H-LABEL_H-8))
        ox = x + (TILE_W-im.width)//2
        oy = y + 4
        sheet.paste(im, (ox, oy))
        dr.rectangle([x, y+TILE_H-LABEL_H, x+TILE_W, y+TILE_H], fill=(30,30,30))
        dr.text((x+8, y+TILE_H-LABEL_H+6), fn.replace(".webp",""), fill="white", font=f1)
        dr.rectangle([x, y, x+TILE_W-1, y+TILE_H-1], outline=(210,210,210))
    os.makedirs(OUT, exist_ok=True)
    p = os.path.join(OUT, f"{nid}.jpg")
    sheet.save(p, quality=80)
    return p

if __name__ == "__main__":
    import sys
    tm = title_map()
    ids = sys.argv[1:] or sorted(os.listdir(IMG_ROOT))
    n = 0
    for nid in ids:
        if build_one(nid, tm): n += 1
    print("sheets:", n)
