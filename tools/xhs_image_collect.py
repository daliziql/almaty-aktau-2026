#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书图片采集共用工具（必须在 mac_computer_use_tool(plane="bu") 单元格内调用）。
- 全程通过浏览器会话访问笔记页、经 bu.download 走浏览器下载，不使用 requests/curl 直连爬取。
- 视频笔记自动跳过；每篇笔记按人类节奏随机停顿。
- 断点续跑：已采集目录非空则跳过。

用法（browser cell 内）:
    import sys; sys.path.insert(0, "/Users/bytedance/workspace/travel-books/tools")
    from xhs_image_collect import collect_batch
    collect_batch(a=0, b=8, cap=8)
"""
import json, os, time, random, shutil, re, sys

TRIP_DIR = "/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
DEEP = os.path.join(TRIP_DIR, "raw/xhs/deep_pick.json")
IMG_ROOT = os.path.join(TRIP_DIR, "raw/xhs/imgs")
META = os.path.join(TRIP_DIR, "raw/xhs/img_meta.jsonl")
DL_DIR = os.path.expanduser("~/Downloads")

EXTRACT_JS = r"""
(()=>{
  const s=window.__INITIAL_STATE__;
  if(!s||!s.note) return {err:'no state'};
  const m=s.note.noteDetailMap||{};
  const id=Object.keys(m)[0];
  if(!id) return {err:'no detail'};
  const n=m[id].note||{};
  return {id:n.noteId, type:n.type, title:n.title||'',
          imgs:(n.imageList||[]).map(im=>im.urlDefault),
          video: n.video?{crc:n.video.crc||null}:null};
})()
"""

def _note_url(href: str) -> str:
    # /search_result/<id>?xsec_token=..&xsec_source=  -> 强制 pc_search，保证可打开
    if href.startswith("http"):
        u = href
    else:
        u = "https://www.xiaohongshu.com" + href
    u = re.sub(r"xsec_source=[^&]*", "xsec_source=pc_search", u)
    if "xsec_source" not in u:
        u += ("&" if "?" in u else "?") + "xsec_source=pc_search"
    return u

def collect_batch(a: int, b: int, cap: int = 8, slow: bool = True):
    import seed_browser_use as bu
    items = json.load(open(DEEP, encoding="utf-8"))
    os.makedirs(IMG_ROOT, exist_ok=True)
    seg = items[a:b]
    logf = open(META, "a", encoding="utf-8")
    for it in seg:
        nid = it["id"]
        ddir = os.path.join(IMG_ROOT, nid)
        if os.path.isdir(ddir) and len(os.listdir(ddir)) > 0:
            print(f"SKIP {nid} (done)")
            continue
        url = _note_url(it["href"])
        try:
            bu.navigate(url)
            bu.wait_for_load(timeout=15)
        except Exception as e:
            print(f"NAV-FAIL {nid}: {e}")
            continue
        time.sleep(random.uniform(2.2, 3.8) if slow else 1.5)
        try:
            info = bu.js(EXTRACT_JS)
        except Exception as e:
            print(f"JS-FAIL {nid}: {e}")
            continue
        if not info or info.get("err"):
            print(f"NO-DETAIL {nid}: {info}")
            continue
        ntype = info.get("type")
        imgs = info.get("imgs") or []
        if ntype == "video" or info.get("video"):
            rec = {"id": nid, "type": "video", "n_imgs": 0, "saved": 0,
                   "title": info.get("title", "")[:50]}
            logf.write(json.dumps(rec, ensure_ascii=False) + "\n"); logf.flush()
            print(f"VIDEO-SKIP {nid} {info.get('title','')[:30]}")
            time.sleep(random.uniform(1.2, 2.2))
            continue
        os.makedirs(ddir, exist_ok=True)
        saved = 0
        for i, iu in enumerate(imgs[:cap]):
            tmp = f"xhs_{nid}_{i}.webp"
            try:
                r = bu.download(iu, filename=tmp)
                time.sleep(random.uniform(0.5, 1.1))
                src = r.get("path") or os.path.join(DL_DIR, tmp)
                if r.get("state") == "completed" and os.path.exists(src):
                    shutil.move(src, os.path.join(ddir, f"img_{i:02d}.webp"))
                    saved += 1
                else:
                    print(f"  DL-INCOMPLETE {nid} {i}: {r.get('state')}")
            except Exception as e:
                print(f"  DL-FAIL {nid} {i}: {e}")
        rec = {"id": nid, "type": ntype, "n_imgs": len(imgs), "saved": saved,
               "title": info.get("title", "")[:50], "kw": it.get("kw")}
        logf.write(json.dumps(rec, ensure_ascii=False) + "\n"); logf.flush()
        print(f"OK {nid} saved={saved}/{len(imgs)} :: {info.get('title','')[:34]}")
        time.sleep(random.uniform(1.6, 3.0))
    logf.close()
    print("BATCH DONE", a, b)

if __name__ == "__main__":
    pass
