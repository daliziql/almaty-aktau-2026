#!/usr/bin/env python3
"""汇总 Trivago MCP + Airbnb MCP 原始结果为 quotes_summary.json。"""
import json, os, re, statistics, sys

D = os.path.abspath(os.path.join(
    os.path.dirname(__file__), "..", "..",
    "trips/2026-10-哈萨克斯坦-阿拉木图阿克套/lodging-data"))
COLLECTED = "2026-09-01"

def load(n): return json.load(open(os.path.join(D, n)))

def cny(s):
    if not s: return None
    m = re.search(r"[\d,]+", str(s))
    return int(m.group().replace(",", "")) if m else None

# ---------- 1. Trivago 种子酒店（两轮合并，优先有价） ----------
r1 = load("trivago_seed_hotels.json")
r2 = load("trivago_seed_hotels_round2.json")
r2map = {"h1": "h1_d8", "h3": "h3_d8", "h4": "h4_d8",
         "h9": "h9b", "h10": "h10b", "h11": "h11b"}
seed_quote = {}
for sid, blk in r1.items():
    item = (blk["items"] or [{}])[0]
    if sid in r2map:  # 第二轮为精确改查/补价，无条件优先
        alt = r2[r2map[sid]]["items"][0]
        if "error" not in alt:
            item = alt if (alt.get("accommodation_name") and
                           (cny(alt.get("price_per_night")) or not cny(item.get("price_per_night"))
                            or sid in ("h10", "h11"))) else item
    alts = []
    if sid in r2map:
        a2 = r2[r2map[sid]]["items"][0]
        if cny(a2.get("price_per_night")):
            alts.append({"date": f"{a2.get('arrival')}~{a2.get('departure')}",
                         "price_cny": cny(a2.get("price_per_night")),
                         "advertiser": a2.get("advertisers")})
    b1 = (blk["items"] or [{}])[0]
    if cny(b1.get("price_per_night")) and (not alts or
        f"{b1.get('arrival')}~{b1.get('departure')}" != alts[0]["date"]):
        alts.insert(0, {"date": f"{b1.get('arrival')}~{b1.get('departure')}",
                        "price_cny": cny(b1.get("price_per_night")),
                        "advertiser": b1.get("advertisers")})
    seed_quote[sid] = {
        "name": item.get("accommodation_name"),
        "price_cny": cny(item.get("price_per_night")),
        "price_stay": item.get("price_per_stay"),
        "alt_quotes": alts,
        "advertiser": item.get("advertisers"),
        "stars": item.get("hotel_rating"),
        "review": item.get("review_rating"),
        "reviews": item.get("review_count"),
        "amenities": item.get("top_amenities"),
        "url": item.get("accommodation_url"),
        "image": item.get("main_image"),
        "lat": item.get("latitude"), "lng": item.get("longitude"),
        "distance": item.get("distance"),
        "sample_date": f"{item.get('arrival')}~{item.get('departure')}",
        "collected": COLLECTED}

# ---------- 2. Trivago 阿拉木图广搜 -> 额外候选（去重合并两晚） ----------
broad = {}
for fn in ["trivago_almaty_1002.json", "trivago_almaty_1008.json"]:
    for h in load(fn):
        n = h.get("accommodation_name", "")
        p = cny(h.get("price_per_night"))
        e = broad.setdefault(n, {"prices": [], "meta": h})
        if p: e["prices"].append(p)
extra = []
seed_names = {v["name"] for v in seed_quote.values()}
for n, e in broad.items():
    h = e["meta"]; ps = e["prices"]
    if n in seed_names or not ps: continue
    extra.append({"name": n, "price_avg": round(statistics.mean(ps)),
                  "prices": ps, "advertiser": h.get("advertisers"),
                  "stars": h.get("hotel_rating"), "review": h.get("review_rating"),
                  "reviews": cny(h.get("review_count")),
                  "amenities": h.get("top_amenities"),
                  "url": h.get("accommodation_url"), "image": h.get("main_image"),
                  "lat": h.get("latitude"), "lng": h.get("longitude")})
extra.sort(key=lambda x: (-(x["reviews"] or 0)))

# ---------- 3. Airbnb 按城市坐标圈过滤 ----------
BOXES = {"almaty": (43.18, 43.36, 76.78, 77.10),       # 阿拉木图市区
         "aktau": (43.55, 43.78, 50.95, 51.35),        # 阿克套市区海岸
         "saty": (42.85, 43.15, 78.15, 78.60)}         # Saty/Kolsay 湖区
def in_box(lat, lng, box):
    if lat is None or lng is None: return False
    a, b, c, d = box
    return a <= lat <= b and c <= lng <= d

abnb = {"almaty": [], "aktau": [], "saty": []}
seen = {"almaty": set()}
a1 = load("airbnb_almaty_1002.json")
cand = list(a1.get("brief", []))
ab = load("airbnb_almaty_batch.json")
for k in ("almaty_a", "almaty_center"):
    cand += ab.get(k, {}).get("brief", [])
for r in cand:
    if r.get("id") in seen["almaty"]: continue
    if in_box(r.get("lat"), r.get("lng"), BOXES["almaty"]):
        seen["almaty"].add(r.get("id")); abnb["almaty"].append(r)
batch = load("airbnb_batch.json")
seen2 = {"saty": set(), "aktau": set()}
for key, fname in [("saty", "saty_kolsai"), ("aktau", "aktau")]:
    for r in batch.get(fname, {}).get("brief", []):
        if r.get("id") in seen2[key]: continue
        if in_box(r.get("lat"), r.get("lng"), BOXES[key]):
            seen2[key].add(r.get("id")); abnb[key].append(r)
for k in abnb: abnb[k].sort(key=lambda r: -(float(re.search(r"[\d.]+", r["rating"] or "0").group()) if r.get("rating") and re.search(r"\d", r["rating"]) else 0))

out = {"collected": COLLECTED, "currency": "CNY",
       "note": "Trivago 官方 MCP 实时聚合报价（含 Booking/Agoda/Trip.com）；Airbnb 社区 MCP 匿名检索，已按坐标过滤城市圈",
       "seed_quotes": seed_quote, "trivago_extra_almaty": extra,
       "airbnb": abnb}
json.dump(out, open(os.path.join(D, "quotes_summary.json"), "w"),
          ensure_ascii=False, indent=1)

print("== 种子酒店报价 ==")
for sid, q in seed_quote.items():
    print(f"{sid:4} {q['name'][:38]:40} ¥{q['price_cny']}  {q['advertiser']}  {q['review']}({q['reviews']})")
print("\n== Airbnb 可用数 ==", {k: len(v) for k, v in abnb.items()})
print("== Trivago 额外阿拉木图候选:", len(extra))
for e in extra[:10]:
    print(f"  {e['name'][:36]:38} ¥{e['price_avg']} {e['advertiser']} {e['review']}({e['reviews']})")
print("\nsaved quotes_summary.json")
