#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""小红书酒店口碑图管线：下载候选 -> 拼联系表(供 AI 逐张视觉审核) -> 保留审核通过的图并压缩。
用法:
  fetch <cand.json>   # cand.json: {"hid":"h10","items":[{"noteId":"..","author":"..","urls":[...]}]}
  keep  <cand.json> <keep.json>  # keep.json: {"h10": ["<noteId>/<idx>.webp", ...]}
"""
import json, os, sys, time, urllib.request, io
from PIL import Image

ROOT = os.path.join(os.path.dirname(__file__), "..", "..",
                    "trips", "2026-10-哈萨克斯坦-阿拉木图阿克套")
LX = os.path.join(ROOT, "assets", "lodge-xhs")
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch_url(url, timeout=25):
    req = urllib.request.Request(url, headers={
        "User-Agent": UA,
        "Referer": "https://www.xiaohongshu.com/",
        "Accept": "image/avif,image/webp,image/*,*/*;q=0.8",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def save_webp(raw, out, max_side=1280, quality=78):
    im = Image.open(io.BytesIO(raw)).convert("RGB")
    if max(im.size) > max_side:
        im.thumbnail((max_side, max_side), Image.LANCZOS)
    im.save(out, "WEBP", quality=quality, method=4)
    return im.size


def sheet(paths, out, cell=340, cols=5):
    from PIL import ImageDraw
    imgs = []
    for p in paths:
        try:
            im = Image.open(p).convert("RGB")
            im.thumbnail((cell, cell), Image.LANCZOS)
            imgs.append((p, im))
        except Exception as e:
            print("skip", p, e)
    if not imgs:
        return
    rows = (len(imgs) + cols - 1) // cols
    pad, label_h = 8, 22
    W = cols * (cell + pad) + pad
    H = rows * (cell + label_h + pad) + pad
    canvas = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(canvas)
    for i, (p, im) in enumerate(imgs):
        r, c = divmod(i, cols)
        x = pad + c * (cell + pad)
        y = pad + r * (cell + label_h + pad)
        canvas.paste(im, (x, y + label_h))
        d.rectangle([x, y, x + cell, y + label_h], fill=(235, 235, 245))
        d.text((x + 4, y + 4), f"#{i} {os.path.basename(os.path.dirname(p))}/{os.path.basename(p)}", fill=(0, 0, 0))
    canvas.save(out, "WEBP", quality=80)
    return out


def cmd_fetch(cand_path):
    cand = json.load(open(cand_path, encoding="utf-8"))
    hid = cand["hid"]
    cdir = os.path.join(LX, hid, "_cand")
    os.makedirs(cdir, exist_ok=True)
    manifest = []
    for it in cand["items"]:
        nid = it["noteId"]
        nd = os.path.join(cdir, nid)
        os.makedirs(nd, exist_ok=True)
        for idx, u in enumerate(it["urls"]):
            out = os.path.join(nd, f"{idx}.webp")
            if os.path.exists(out):
                manifest.append(out); continue
            try:
                raw = fetch_url(u)
                save_webp(raw, out)
                manifest.append(out)
                print("ok", nid, idx, len(raw))
                time.sleep(0.8)
            except Exception as e:
                print("FAIL", nid, idx, repr(e)[:120])
    if manifest:
        sh = os.path.join(cdir, "_sheet.webp")
        sheet(manifest, sh)
        print("SHEET", sh, "n=", len(manifest))


def cmd_keep(cand_path, keep_path):
    keep = json.load(open(keep_path, encoding="utf-8"))
    cand = json.load(open(cand_path, encoding="utf-8"))
    hid = cand["hid"]
    wants = set(keep.get(hid, []))
    dst = os.path.join(LX, hid)
    os.makedirs(dst, exist_ok=True)
    kept, dropped = [], []
    for root, _, files in os.walk(os.path.join(dst, "_cand")):
        for f in files:
            if f == "_sheet.webp":
                continue
            rel = os.path.relpath(os.path.join(root, f), os.path.join(dst, "_cand"))
            src = os.path.join(root, f)
            if rel in wants:
                outp = os.path.join(dst, f"{os.path.dirname(rel)}_{f}")
                if not os.path.exists(outp):
                    Image.open(src).save(outp, "WEBP", quality=78, method=4)
                kept.append(outp)
            else:
                dropped.append(src)
    for p in dropped:
        try: os.remove(p)
        except OSError:
            pass
    print("KEPT", len(kept))
    for p in sorted(kept):
        print(" ", os.path.basename(p))


if __name__ == "__main__":
    if sys.argv[1] == "fetch":
        cmd_fetch(sys.argv[2])
    elif sys.argv[1] == "keep":
        cmd_keep(sys.argv[2], sys.argv[3])
    else:
        print(__doc__)
