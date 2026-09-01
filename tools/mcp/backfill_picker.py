#!/usr/bin/env python3
"""用 quotes_summary.json（MCP 采集结果）回填住宿选型.html 的 SEED / SEED_QUOTES。
- 保留人工撰写的 pros/cons/colleague/tags 等文案，只改价格/评分/备注/图片/报价
- 新增 Trivago 额外酒店候选与 Airbnb 高分民宿候选
- 平台图下载到 assets/hotels/ 本地化，避免外链依赖
"""
import json, os, re, urllib.request, ssl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
TRIP = os.path.join(ROOT, "trips/2026-10-哈萨克斯坦-阿拉木图阿克套")
HTML = os.path.join(TRIP, "住宿选型.html")
DATA = json.load(open(os.path.join(TRIP, "lodging-data/quotes_summary.json")))
IMGDIR = os.path.join(TRIP, "assets/hotels")
os.makedirs(IMGDIR, exist_ok=True)
COL = DATA["collected"]
ctx = ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE

def dl_img(url, sid):
    if not url: return ""
    fn = f"{sid}.jpg"; p = os.path.join(IMGDIR, fn)
    if not os.path.exists(p):
        try:
            req = urllib.request.Request(url, headers={"Referer": "https://www.trivago.com/",
                                                        "User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30, context=ctx) as r, open(p, "wb") as f:
                f.write(r.read())
        except Exception as e:
            print("img fail", sid, e); return ""
    return f"assets/hotels/{fn}"

def adv2key(adv):
    return {"Trip.com": "trip", "Booking.com": "booking", "Agoda": "agoda"}.get(adv, "booking")

html = open(HTML, encoding="utf-8").read()
orig = html

# ---------- 1. PLATFORMS 增加 Agoda ----------
html = html.replace(
    "const PLATFORMS=[['trip','Trip.com'],['airbnb','Airbnb'],['booking','Booking']];",
    "const PLATFORMS=[['trip','Trip.com'],['airbnb','Airbnb'],['booking','Booking'],['agoda','Agoda']];")
html = html.replace(
    "  booking:n=>'https://www.booking.com/searchresults.html?ss='+encodeURIComponent(n)\n};",
    "  booking:n=>'https://www.booking.com/searchresults.html?ss='+encodeURIComponent(n),\n"
    "  agoda:n=>'https://www.agoda.com/search?searchText='+encodeURIComponent(n)\n};")
# 新增候选初始化也带上 agoda（两处）
html = html.replace("{trip:{price:null,date:'',url:''},airbnb:{price:null,date:'',url:''},booking:{price:null,date:'',url:''}}",
                    "{trip:{price:null,date:'',url:''},airbnb:{price:null,date:'',url:''},booking:{price:null,date:'',url:''},agoda:{price:null,date:'',url:''}}")
# 攻略参考文案
html = html.replace("约 ¥${h.refPrice}/晚（区间估值，待平台核验）",
                    "¥${h.refPrice}/晚（MCP 实时核验 ${h.mcpDate||''}）")

# ---------- 2. 切分 SEED 块，逐 id 更新 ----------
m = re.search(r"const SEED=\[", html)
start = m.end()
# 找到匹配的结束 "];"（种子结束标记是 "\n];\n/* 平台报价"）
end = html.index("];", start)
head, body, tail = html[:start], html[start:end], html[end:]

def split_blocks(b):
    # 每个对象以 "\n {id:'" 开始
    idxs = [mm.start() for mm in re.finditer(r"\n \{id:'", b)]
    out = []
    for i, s in enumerate(idxs):
        e = idxs[i + 1] if i + 1 < len(idxs) else len(b)
        out.append((b[s:e], s, e))
    return out

sq = DATA["seed_quotes"]
quotes_js = {}
new_blocks = []
for blk, s, e in split_blocks(body):
    mid = re.search(r"id:'(h\d+)'", blk).group(1)
    q = sq.get(mid)
    if not q:
        new_blocks.append(blk); continue
    # 下载平台图
    local = dl_img(q.get("image"), mid)
    # refPrice / rating
    price = q.get("price_cny")
    review = float(q["review"]) if q.get("review") and re.match(r"^[\d.]+$", str(q["review"])) else None
    if price:
        blk = re.sub(r"refPrice:\d+", f"refPrice:{price}", blk, count=1)
    if review:
        blk = re.sub(r"rating:[\d.]+", f"rating:{round(review/2,1)}", blk, count=1)
    blk = re.sub(r"mcpDate:'[^']*',", "", blk)
    blk = blk.replace("status:'", f"mcpDate:'{COL}',status:'", 1)
    # imgs 前插入平台图
    if local and "assets/hotels/" not in blk:
        cap = f"MCP 聚合平台图（来源 {q.get('advertiser')}，{COL}）"
        blk = blk.replace("imgs:[", f"imgs:[\n   {{src:'{local}',cap:'{cap}',url:'{q.get('url','')}'}},", 1)
    # note 追加核验信息
    alt = q.get("alt_quotes") or []
    note_txt = f"MCP核验{COL[5:]}：{q.get('advertiser')} ¥{price}/晚" + (
        f"，另样本 {alt[0]['date'][5:]} ¥{alt[0]['price_cny']}" if len(alt) > 1 else "")
    note_txt += f"；平台评分 {q.get('review')}（{q.get('reviews')}条）" if review else "；平台暂无评分/报价，待人工核"
    blk = re.sub(r"note:'([^']*)'", lambda mm: f"note:'{mm.group(1)}；{note_txt}'" if mm.group(1) else f"note:'{note_txt}'",
                 blk, count=1)
    # 报价结构
    qobj = {k: {"price": None, "date": "", "url": ""} for k in ("trip", "airbnb", "booking", "agoda")}
    if price:
        k = adv2key(q.get("advertiser"))
        qobj[k] = {"price": price, "date": COL, "url": q.get("url", "")}
    for a in alt:
        k2 = adv2key(a["advertiser"])
        if qobj[k2]["price"] is None:
            qobj[k2] = {"price": a["price_cny"], "date": COL, "url": q.get("url", "")}
    quotes_js[mid] = qobj
    new_blocks.append(blk)

# ---------- 3. 追加 Trivago 额外酒店候选 ----------
def esc(s): return (s or "").replace("'", "\\'").replace("\n", " ")
extra_pick = ["Hotel Kazakhstan", "The Dostyk Hotel", "Hotel Uyut Almaty",
              "Grand Voyage Hotel", "Ramada by Wyndham Almaty", "ibis Almaty Jetisu",
              "Novotel Almaty City Center", "Grand Tien Shan Hotel"]
eid = 13
for e in DATA["trivago_extra_almaty"]:
    if e["name"] not in extra_pick: continue
    sid = f"h{eid}"; eid += 1
    local = dl_img(e.get("image"), sid)
    rev = float(e["review"]) if re.match(r"^[\d.]+$", str(e.get("review"))) else None
    qobj = {k: {"price": None, "date": "", "url": ""} for k in ("trip", "airbnb", "booking", "agoda")}
    k = adv2key(e["advertiser"]); qobj[k] = {"price": e["price_avg"], "date": COL, "url": e.get("url", "")}
    quotes_js[sid] = qobj
    new_blocks.append(
        f"\n {{id:'{sid}',city:'almaty',name:'{esc(e['name'])}',en:'{esc(e['name'])}',area:'MCP 扩展候选',tier:'中端',"
        f"refPrice:{e['price_avg']},rating:{round(rev/2,1) if rev else 0},xhsCnt:'',tags:'MCP新增,待实地评估',"
        f"colleague:'',xhs:'',pros:'平台评论 {e['reviews']} 条，评分 {e['review']}\\n设施：{esc(e.get('amenities'))}',cons:'',"
        f"imgs:" + (f"[{{src:'{local}',cap:'MCP 聚合平台图（{esc(e['advertiser'])}）',url:'{e.get('url','')}'}}]" if local else "[]")
        + f",nights:'D1-D2,D4,D7',mcpDate:'{COL}',status:'candidate',note:'MCP 扩展候选，两晚均价 {e['prices']}'"
        + "},")

# ---------- 4. 追加 Airbnb 高分民宿候选 ----------
def parse_price(s):
    m = re.search(r"¥([\d,]+)", s or ""); return int(m.group(1).replace(",", "")) if m else None
ab_pick = {
    "almaty": ["Apartment on Arbat 21", "Apartment near Mega Park", "Luxe Corner at Meridian 154",
               "Sunlit Designer Apartment near Botanical Garden"],
    "aktau": ["Seaside apartment", "The best location!", "Cozy studio in Premium Plaza residential complex",
              "Clean and cozy apartment"],
    "saty": ["Mountain View - Kolsay", '"Bereke" - Kaindy lake wooden cabin', "Glamping Kolsay",
             "Kolsai A-Frame AI-ADIL"],
}
aid = 1
nights_map = {"almaty": "D1-D2,D4,D7", "aktau": "D5-D6", "saty": "D3"}
nights_n = {"almaty": 1, "aktau": 2, "saty": 1}
for city, names in ab_pick.items():
    for r in DATA["airbnb"][city]:
        if r["name"] not in names: continue
        sid = f"ab{aid}"; aid += 1
        total = parse_price(r.get("price")); pernight = round(total / nights_n[city]) if total else 0
        qobj = {k: {"price": None, "date": "", "url": ""} for k in ("trip", "airbnb", "booking", "agoda")}
        qobj["airbnb"] = {"price": pernight, "date": COL, "url": r.get("url", "")}
        quotes_js[sid] = qobj
        rating = re.search(r"([\d.]+) out of 5", r.get("rating") or "")
        rev_n = re.search(r",\s*([\d,]+) reviews", r.get("rating") or "")
        new_blocks.append(
            f"\n {{id:'{sid}',city:'{city}',name:'Airbnb · {esc(r['name'])}',en:'',area:'Airbnb 高分民宿',tier:'民宿',"
            f"refPrice:{pernight},rating:{rating.group(1) if rating else 0},xhsCnt:'',tags:'Airbnb,{esc(r.get('badges') or '')},{esc(r.get('beds'))}',"
            f"colleague:'',xhs:'',pros:'{esc(r.get('rating'))}',cons:'民宿无前台，入住需线上沟通；下单前看退订政策',"
            f"imgs:[],nights:'{nights_map[city]}',mcpDate:'{COL}',status:'candidate',note:'Airbnb 总价 {esc(r.get('price'))}"
            + (f"，{rev_n.group(1)}条评论" if rev_n else "") + "'},")

body_new = "".join(b.rstrip().rstrip(",") + ",\n" for b in new_blocks).rstrip().rstrip(",")
html = head + body_new + tail

# ---------- 5. 重写 SEED_QUOTES ----------
lines = ["const SEED_QUOTES={};",
         "SEED.forEach(h=>{SEED_QUOTES[h.id]={trip:{price:null,date:'',url:''},airbnb:{price:null,date:'',url:''},booking:{price:null,date:'',url:''},agoda:{price:null,date:'',url:''}}});",
         "const MCP_QUOTES=" + json.dumps(quotes_js, ensure_ascii=False, indent=1).replace("\n", "\n") + ";",
         "Object.assign(SEED_QUOTES,Object.fromEntries(Object.entries(MCP_QUOTES).map(([k,v])=>[k,Object.assign(SEED_QUOTES[k],v)])));"]
sq_block = "\n".join(lines)
html = re.sub(r"const SEED_QUOTES=\{\};\s*\nSEED\.forEach\(h=>\{SEED_QUOTES\[h\.id\]=\{.*?\}\}\);",
              sq_block, html, count=1, flags=re.S)

open(HTML, "w", encoding="utf-8").write(html)
print("回填完成，新增酒店候选:", eid - 13, "民宿候选:", aid - 1, "报价条目:", len(quotes_js))
print("文件大小:", len(html))
