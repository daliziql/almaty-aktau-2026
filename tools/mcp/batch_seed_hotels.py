#!/usr/bin/env python3
"""按住宿选型种子逐家精确查询 Trivago MCP，结果合并落盘。"""
import json, sys, time, os
sys.path.insert(0, os.path.dirname(__file__))
from trivago_mcp_client import TrivagoMCP

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "..",
    "trips/2026-10-哈萨克斯坦-阿拉木图阿克套/lodging-data")
OUT_DIR = os.path.abspath(OUT_DIR)

# (种子id, 检索词, 入住, 退房)
TARGETS = [
    ("h1", "Renion City Hotel Almaty", "2026-10-02", "2026-10-03"),
    ("h2", "Kazzhol Hotel Almaty", "2026-10-02", "2026-10-03"),
    ("h3", "Holiday Inn Almaty", "2026-10-02", "2026-10-03"),
    ("h4", "Ritz-Carlton Almaty", "2026-10-02", "2026-10-03"),
    ("h5", "Interhouse Almaty", "2026-10-02", "2026-10-03"),
    ("h8", "Caspian Riviera Grand Palace Aktau", "2026-10-06", "2026-10-08"),
    ("h9", "Holiday Inn Aktau", "2026-10-06", "2026-10-08"),
    ("h10", "Renaissance Aktau Hotel", "2026-10-06", "2026-10-08"),
    ("h11", "Tarlan Hotel Aktau", "2026-10-06", "2026-10-08"),
    ("h12", "Rixos Water World Aktau", "2026-10-06", "2026-10-08"),
]

def main():
    c = TrivagoMCP()
    allres = {}
    for sid, q, arr, dep in TARGETS:
        try:
            txt = c.call_tool("trivago-accommodation-search", {
                "query": q, "arrival": arr, "departure": dep,
                "adults": 2, "rooms": 1, "currency": "CNY",
                "language": "EN_US", "country": "HK"})
            items = c.parse_output(txt)
        except Exception as e:
            items = [{"error": str(e)}]
        allres[sid] = {"query": q, "arrival": arr, "departure": dep, "items": items}
        print(f"== {sid} {q}: {len(items)} 条")
        for h in items[:4]:
            if "error" in h: print("   ERR", h["error"][:120]); continue
            print("   -", h.get("accommodation_name"), "|", h.get("price_per_night"),
                  "|", h.get("advertisers"), "|", h.get("review_rating"), h.get("review_count"))
        time.sleep(2.0)  # 低频，礼貌间隔
    out = os.path.join(OUT_DIR, "trivago_seed_hotels.json")
    json.dump(allres, open(out, "w"), ensure_ascii=False, indent=1)
    print("saved:", out)

if __name__ == "__main__":
    main()
