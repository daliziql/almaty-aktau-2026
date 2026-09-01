#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书「按关键点定向搜索 · 人工点击式」采集 v3（必须在 mac_computer_use_tool(plane="bu") 内调用）。
防漂移设计：
- 每次取卡前强制校验当前是该关键词的搜索结果页（URL 含 search_result），否则重新导航
- 真实 bu.click 点卡进入后校验 URL 含目标笔记 id，否则判失败
- 不依赖 history back：处理完一篇一律重新导航搜索页（等同用户重新搜索，确定性恢复）
- must 严格模式：给出 must 词时，只收标题命中的笔记，杜绝推荐流/泛攻略混入
- 全局 seen 去重，同一笔记只归属一个实体；输出独立目录 raw/xhs/imgs2/<key>/
"""
import json, os, time, random, shutil, re, urllib.parse

TRIP_DIR = "/Users/bytedance/workspace/travel-books/trips/2026-10-哈萨克斯坦-阿拉木图阿克套"
ROOT2 = os.path.join(TRIP_DIR, "raw/xhs/imgs2")
SEEN_F = os.path.join(TRIP_DIR, "raw/xhs/imgs2_seen.json")
LOG_F = os.path.join(TRIP_DIR, "raw/xhs/imgs2_meta.jsonl")
DBG = "/tmp/xc_debug.log"
DL_DIR = os.path.expanduser("~/Downloads")
os.makedirs(ROOT2, exist_ok=True)

CARD_JS = r"""
(()=>{
 if(!location.href.includes('search_result')) return {bad:location.href};
 return {ok:[...document.querySelectorAll('section.note-item')].map(c=>{
  const a=c.querySelector('a.cover'); if(!a) return null;
  const href=a.getAttribute('href')||'';
  const title=((c.querySelector('.title')||c.querySelector('.footer .title')||{}).textContent||'').trim();
  const like=((c.querySelector('.like-wrapper .count')||c.querySelector('.count')||{}).textContent||'').trim();
  const m=href.match(/(?:explore|search_result)\/([0-9a-f]+)/);
  return m?{id:m[1],title,like}:null;
 }).filter(Boolean)};
})()
"""
IMG_JS = r"""
(()=>{
  const video=!!(document.querySelector('video')||document.querySelector('.player-container')||document.querySelector('.xgplayer'));
  let imgs=[...document.querySelectorAll('.swiper-slide img')].map(i=>i.src||i.getAttribute('data-src'));
  if(!imgs.length) imgs=[...document.querySelectorAll('.note-content img,.media-container img')].map(i=>i.src);
  imgs=imgs.filter(u=>u&&u.includes('xhscdn')&&!u.includes('avatar'));
  imgs=[...new Set(imgs)];
  const title=((document.querySelector('#detail-title')||{}).textContent||'').trim();
  return {video,imgs,title,url:location.href};
})()
"""

def _dbg(msg):
    with open(DBG,"a",encoding="utf-8") as f: f.write(msg+"\n")
def _load_seen():
    return json.load(open(SEEN_F,encoding="utf-8")) if os.path.exists(SEEN_F) else {}
def _save_seen(seen):
    json.dump(seen,open(SEEN_F,"w",encoding="utf-8"),ensure_ascii=False,indent=1)
def _like_num(s):
    s=(s or "").strip()
    if not s: return 0
    try:
        if s.endswith("万"): return int(float(s[:-1])*10000)
        if s.lower().endswith("k"): return int(float(s[:-1])*1000)
        return int(float(s))
    except Exception: return 0

def goto_search(bu, kw, scrolls=2):
    """强制导航到搜索页并返回去重、按赞排序的卡片。"""
    q=urllib.parse.quote(kw)
    url=f"https://www.xiaohongshu.com/search_result?keyword={q}&source=web_search_result_notes"
    bu.navigate(url); bu.wait_for_load(timeout=15)
    time.sleep(random.uniform(2.0,3.0))
    for _ in range(scrolls):
        bu.js("window.scrollBy(0,850)"); time.sleep(random.uniform(1.1,1.8))
    r=bu.js(CARD_JS)
    if not r or r.get("bad"):
        _dbg(f"goto_search bad page: {r}"); time.sleep(2)
        bu.navigate(url); bu.wait_for_load(timeout=15); time.sleep(2.5)
        r=bu.js(CARD_JS)
    cards=(r or {}).get("ok") or []
    uniq={}
    for c in cards: uniq.setdefault(c["id"],c)
    return sorted(uniq.values(),key=lambda c:_like_num(c.get("like")),reverse=True)

def _ref_for(bu, nid):
    bu.js(f"(()=>{{const a=document.querySelector('a.cover[href*=\"{nid}\"]');if(a)a.scrollIntoView({{block:'center'}});}})()")
    time.sleep(0.8)
    for _ in range(2):
        snap=bu.snapshot()
        text=snap if isinstance(snap,str) else json.dumps(snap,ensure_ascii=False)
        for line in text.splitlines():
            if nid in line and "->" in line:
                m=re.match(r"\s*(d\d+:e\d+)\b",line)
                if m: return m.group(1)
        time.sleep(0.8)
    return None

def enter_note(bu, nid, ref):
    bu.click(ref)
    info=None
    for _ in range(8):
        time.sleep(0.85)
        url=bu.js("location.href") or ""
        if nid not in url: continue
        info=bu.js(IMG_JS)
        if info and (info.get("video") or info.get("imgs")): return info
    return info

def run_entity(key, keywords, n_notes=4, cap=6, must=None, strict=True):
    import seed_browser_use as bu
    kdir=os.path.join(ROOT2,key); os.makedirs(kdir,exist_ok=True)
    seen=_load_seen(); logf=open(LOG_F,"a",encoding="utf-8")
    picked,tried=[],set()
    def title_ok(t):
        if not must: return True
        tl=t.lower()
        return any(m.lower() in tl for m in must)
    for kw in keywords:
        if len(picked)>=n_notes: break
        _dbg(f"== {key} :: {kw}")
        try:
            cards=goto_search(bu,kw)
        except Exception as e:
            _dbg(f"search-fail {e}"); continue
        print(f"[{key}] '{kw}' cards={len(cards)}")
        for c in cards:
            if len(picked)>=n_notes: break
            nid=c["id"]
            if nid in tried or nid in seen: continue
            if must and strict and not title_ok(c.get("title","")):
                _dbg(f"title-skip {c.get('title','')[:30]}"); continue
            existing=os.path.join(kdir,nid)
            if os.path.isdir(existing) and os.listdir(existing):
                tried.add(nid); picked.append(nid); seen[nid]=key; continue
            tried.add(nid)
            time.sleep(random.uniform(0.9,1.7))
            try:
                ref=_ref_for(bu,nid)
                if not ref: _dbg(f"no-ref {nid}"); continue
                info=enter_note(bu,nid,ref)
            except Exception as e:
                _dbg(f"enter-exc {nid} {e}"); info=None
            # 每次都重新导航回搜索页（确定性恢复，杜绝推荐流漂移）
            try: cards=goto_search(bu,kw,scrolls=1)
            except Exception: pass
            if not info:
                _dbg(f"empty {nid}"); continue
            if info.get("video"):
                _dbg(f"video {nid}"); continue
            # 双保险：笔记自身标题也要过 must
            if must and strict and not title_ok(info.get("title","")) and not title_ok(c.get("title","")):
                _dbg(f"note-title-skip {info.get('title','')[:30]}"); continue
            imgs=info.get("imgs") or []
            _dbg(f"note {nid} imgs={len(imgs)} t={info.get('title','')[:24]}")
            ndir=os.path.join(kdir,nid); os.makedirs(ndir,exist_ok=True)
            saved=0
            for i,u in enumerate(imgs[:cap]):
                tmp=f"xt_{nid}_{i}.webp"
                try:
                    r=bu.download(u,filename=tmp)
                    time.sleep(random.uniform(0.35,0.7))
                    src=r.get("path") or os.path.join(DL_DIR,tmp)
                    if r.get("state")=="completed" and os.path.exists(src):
                        shutil.move(src,os.path.join(ndir,f"img_{i:02d}.webp")); saved+=1
                except Exception as e:
                    _dbg(f"dl-fail {i} {str(e)[:80]}")
            if saved:
                picked.append(nid); seen[nid]=key
                logf.write(json.dumps({"key":key,"id":nid,"saved":saved,
                    "title":(info.get("title") or c.get("title",""))[:60],
                    "search_kw":kw,"like":c.get("like","")},ensure_ascii=False)+"\n"); logf.flush()
                _save_seen(seen)
                print(f"  OK {nid} x{saved} like={c.get('like')} {(info.get('title') or '')[:22]}")
            _dbg(f"done {nid} saved={saved}")
    logf.close()
    tot=sum(len(os.listdir(os.path.join(kdir,d))) for d in os.listdir(kdir))
    print(f"== [{key}] notes={len(picked)} imgs={tot}")
