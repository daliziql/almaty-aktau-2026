#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二步·进帖取正文+下图（后台可跑版）。
Gate-1 批准的笔记在扫描阶段已捕获其 xsec_token（即点击卡片会跳到的同一 URL），
直接用浏览器正常导航到该笔记页（与点击等价：同 URL/同登录态/同渲染，非 HTML 爬虫、非直连 CDN），
读取正文与轮播图，bu.download 经浏览器下载落盘；视频跳过。
可断点续跑（已有 note.json 的笔记跳过）。
browser cell:
  from xhs_fetch import fetch_entities
  fetch_entities(["cathedral"])
"""
import json, os, time, random, shutil

TRIP_DIR="/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
SCAN=os.path.join(TRIP_DIR,"raw/xhs/scan")
ROOT=os.path.join(TRIP_DIR,"raw/xhs/imgs2"); os.makedirs(ROOT,exist_ok=True)
APPROVED="/Users/bytedance/workspace/travel-books/tools/gate1_approved.json"
DL=os.path.expanduser("~/Downloads")
CAP=8

DETAIL_JS=r"""
(()=>{
  const video=!!(document.querySelector('video')||document.querySelector('.player-container')||document.querySelector('.xgplayer'));
  let imgs=[...document.querySelectorAll('.swiper-slide img')].map(i=>i.src||i.getAttribute('data-src'));
  if(!imgs.length) imgs=[...document.querySelectorAll('.note-content img,.media-container img')].map(i=>i.src);
  imgs=[...new Set((imgs||[]).filter(u=>u&&u.includes('xhscdn')&&!u.includes('avatar')))];
  const q=s=>(document.querySelector(s)||{}).textContent||'';
  return {video,imgs,title:q('#detail-title').trim(),desc:q('#detail-desc').trim(),url:location.href};
})()
"""

def _approved(): return json.load(open(APPROVED,encoding="utf-8"))

def _open_note(bu,nid,token,tries=2):
    url=f"https://www.xiaohongshu.com/search_result/{nid}?xsec_token={token}&xsec_source=pc_search"
    for t in range(tries):
        bu.navigate(url); bu.wait_for_load(timeout=15); time.sleep(2.2)
        for _ in range(6):
            cur=bu.js("location.href") or ""
            if nid in cur or "/explore/" in cur:
                info=bu.js(DETAIL_JS)
                if info and (info.get("video") or info.get("imgs")): return info
            time.sleep(0.8)
        time.sleep(1.2)
    return None

def fetch_one(bu,key):
    appr=_approved().get(key,[])
    scan=json.load(open(os.path.join(SCAN,key+".json"),encoding="utf-8"))
    cands=scan["candidates"]
    notes=[cands[i] for i in appr if i<len(cands)]
    kdir=os.path.join(ROOT,key); os.makedirs(kdir,exist_ok=True)
    done=0
    for c in notes:
        nid=c["id"]; ndir=os.path.join(kdir,nid); mark=os.path.join(ndir,"note.json")
        if os.path.exists(mark): done+=1; continue
        if not c.get("token"):
            print(f"  [{key}] no-token {nid}"); continue
        try:
            info=_open_note(bu,nid,c["token"])
            if not info: print(f"  [{key}] open-fail {nid}"); continue
            if info.get("video"):
                print(f"  [{key}] video skip {nid}"); os.makedirs(ndir,exist_ok=True)
                json.dump({"id":nid,"key":key,"video":True,"title":info.get("title","")},
                          open(mark,"w",encoding="utf-8"),ensure_ascii=False); done+=1; continue
            os.makedirs(ndir,exist_ok=True); saved=0
            for i,u in enumerate((info.get("imgs") or [])[:CAP]):
                tmp=f"xf_{nid}_{i}.webp"
                try:
                    r=bu.download(u,filename=tmp); time.sleep(random.uniform(0.25,0.5))
                    src=r.get("path") or os.path.join(DL,tmp)
                    if r.get("state")=="completed" and os.path.exists(src):
                        shutil.move(src,os.path.join(ndir,f"img_{i:02d}.webp")); saved+=1
                except Exception as e:
                    print("  dl-fail",str(e)[:70])
            json.dump({"id":nid,"key":key,"title":info.get("title",c.get("title","")),
                       "desc":(info.get("desc") or "")[:1500],"url":info.get("url"),
                       "like":c.get("like"),"kw":c.get("kw"),"saved":saved},
                      open(mark,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
            done+=1
            print(f"  [{key}] {nid} imgs={saved} {(info.get('title') or '')[:26]}")
            time.sleep(random.uniform(0.8,1.4))
        except Exception as e:
            print(f"  [{key}] FAIL {nid} {repr(e)[:90]}")
    print(f"== [{key}] notes done {done}/{len(notes)}")

def fetch_entities(keys):
    import seed_browser_use as bu
    for k in keys:
        try: fetch_one(bu,k)
        except Exception as e: print(f"[{k}] ENTITY-FAIL",repr(e)[:120])
