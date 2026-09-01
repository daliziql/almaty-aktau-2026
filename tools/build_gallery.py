#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 xhs_gallery_select.json 把核验通过的图片复制到 assets/gallery/<key>/，并生成溯源清单。"""
import json, os, shutil

BASE = "/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
RAW = os.path.join(BASE, "raw/xhs/imgs")
OUT = os.path.join(BASE, "assets/gallery")
SEL = "/Users/bytedance/workspace/travel-books/tools/xhs_gallery_select.json"
NOTES = os.path.join(BASE, "raw/xhs/notes_read.jsonl")
CAP = 24  # 单栏目最多保留张数（均匀抽稀）

def load_notes():
    m = {}
    for line in open(NOTES, encoding="utf-8"):
        d = json.loads(line)
        m[d["id"]] = d
    return m

def capped(entries):
    total = sum(len(e["idx"]) for e in entries)
    if total <= CAP:
        return [(e["id"], i) for e in entries for i in e["idx"]]
    # 轮询抽稀
    queues = {e["id"]: list(e["idx"]) for e in entries}
    picked, seen = [], set()
    while len(picked) < CAP:
        progressed = False
        for nid, q in queues.items():
            if q:
                i = q.pop(0)
                if (nid, i) not in seen:
                    picked.append((nid, i)); seen.add((nid, i)); progressed = True
                    if len(picked) >= CAP: break
        if not progressed: break
    return picked

def main():
    sel = json.load(open(SEL, encoding="utf-8"))
    notes = load_notes()
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    prov = {}
    total = 0
    for key, entries in sel.items():
        if key.startswith("_"): continue
        kdir = os.path.join(OUT, key); os.makedirs(kdir)
        pairs = capped(entries)
        prov[key] = []
        for n, (nid, idx) in enumerate(pairs):
            src = os.path.join(RAW, nid, f"img_{idx:02d}.webp")
            if not os.path.exists(src):
                print("MISSING", src); continue
            fn = f"{key}_{n:02d}_{nid}_{idx:02d}.webp"
            shutil.copy(src, os.path.join(kdir, fn))
            nt = notes.get(nid, {})
            prov[key].append({
                "file": fn, "note_id": nid, "idx": idx,
                "title": nt.get("title", ""), "author": nt.get("author", ""),
                "url": f"https://www.xiaohongshu.com/explore/{nid}",
                "date": nt.get("date", ""), "like": (nt.get("stats") or [""])[0]
            })
            total += 1
        print(f"{key:22s} {len(prov[key])}")
    json.dump(prov, open(os.path.join(OUT, "provenance.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    print("TOTAL selected:", total)

if __name__ == "__main__":
    main()
