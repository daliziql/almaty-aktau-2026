#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第一步·扫描：只做关键词搜索并保存候选帖（id/标题/点赞），不进帖、不下图。
输出 raw/xhs/scan/<key>.json，供 MainAgent 做 Gate-1（帖子相关性 AI 审核）。
browser cell 用法：
  from xhs_scan import scan_entities
  scan_entities(["cathedral","memorial_park"])
"""
import json, os, time, random, urllib.parse

TRIP_DIR="/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
PLAN="/Users/bytedance/workspace/travel-books/tools/entity_plan.json"
OUT=os.path.join(TRIP_DIR,"raw/xhs/scan"); os.makedirs(OUT,exist_ok=True)

CARD_JS=r"""
(()=>{
 if(!location.href.includes('search_result')) return {bad:location.href};
 return {ok:[...document.querySelectorAll('section.note-item')].map(c=>{
  const a=c.querySelector('a.cover'); if(!a) return null;
  const href=a.getAttribute('href')||'';
  const title=((c.querySelector('.title')||c.querySelector('.footer .title')||{}).textContent||'').trim();
  const like=((c.querySelector('.like-wrapper .count')||c.querySelector('.count')||{}).textContent||'').trim();
  const author=((c.querySelector('.author-wrapper .name')||c.querySelector('.name')||{}).textContent||'').trim();
  const m=href.match(/(?:explore|search_result)\/([0-9a-f]+)/);
  const tok=(href.match(/xsec_token=([^&]+)/)||[None,None])[1];
  return m?{id:m[1],title,like,author,token:tok}:null;
 }).filter(Boolean)};
})()
"""

def _like(s):
    s=(s or "").strip()
    try:
        if s.endswith("万"): return int(float(s[:-1])*1e4)
        if s.lower().endswith("k"): return int(float(s[:-1])*1e3)
        return int(float(s))
    except: return 0

def load_plan():
    return {e["key"]:e for e in json.load(open(PLAN,encoding="utf-8"))["entities"]}

def scan_one(bu, ent, topn=12):
    merged={}
    for kw in ent["kws"]:
        q=urllib.parse.quote(kw)
        url=f"https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes"
        bu.navigate(url); bu.wait_for_load(timeout=15); time.sleep(random.uniform(3.2,4.2))
        for _ in range(2):
            bu.js("window.scrollBy(0,800)"); time.sleep(random.uniform(1.4,2.2))
        r=bu.js(CARD_JS)
        if not r or r.get("bad"):
            time.sleep(2); bu.navigate(url); bu.wait_for_load(); time.sleep(3.0); r=bu.js(CARD_JS)
        # 频控冷却：出现“请求太频繁”则等 70s 再试一次
        body=(bu.js("document.body?document.body.innerText:''") or "")
        if "请求太频繁" in body or ("安全验证" in (bu.js("document.title") or "") and not (r or {}).get("ok")):
            print("   ~rate-limited, cooldown 70s"); time.sleep(70)
            bu.navigate(url); bu.wait_for_load(timeout=15); time.sleep(3.5)
            bu.js("window.scrollBy(0,800)"); time.sleep(1.8)
            r=bu.js(CARD_JS)
        for c in (r or {}).get("ok",[]):
            if c["id"] not in merged: c["kw"]=kw; merged[c["id"]]=c
        time.sleep(random.uniform(2.6,3.8))
    cards=list(merged.values())
    must=[m.lower() for m in ent.get("must",[])]
    def hits(t): return any(m in t.lower() for m in must) if must else True
    head=sorted([c for c in cards if hits(c["title"])],key=lambda c:-_like(c["like"]))
    tail=sorted([c for c in cards if not hits(c["title"])],key=lambda c:-_like(c["like"]))
    out=(head+tail)[:topn]
    json.dump({"key":ent["key"],"zh":ent["zh"],"candidates":out},
              open(os.path.join(OUT,ent["key"]+".json"),"w",encoding="utf-8"),
              ensure_ascii=False,indent=1)
    print(f"[{ent['key']}] total={len(cards)} titlehit={len(head)} saved={len(out)}")
    for c in out[:6]: print("   ",c["like"],c["title"][:34])

def scan_entities(keys):
    import seed_browser_use as bu
    plan=load_plan()
    for ii,k in enumerate(keys):
        try: scan_one(bu,plan[k])
        except Exception as e: print(f"[{k}] FAIL",repr(e)[:120])
        if ii<len(keys)-1: time.sleep(random.uniform(6.0,9.0))
