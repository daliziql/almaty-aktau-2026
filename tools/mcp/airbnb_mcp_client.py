#!/usr/bin/env python3
"""Airbnb 社区 MCP（@openbnb/mcp-server-airbnb）本地 stdio 客户端，免登录、免 key。

用法:
  python3 airbnb_mcp_client.py search "Almaty, Kazakhstan" 2026-10-02 2026-10-03 \
      [--adults 2] [--limit 30] [--out a.json]
  python3 airbnb_mcp_client.py details <listingId> 2026-10-02 2026-10-03 [--out d.json]

性质说明（重要）:
- Airbnb 无官方 MCP；该 server 调 Airbnb 公开搜索接口，匿名、不使用任何账号 cookie，
  因此不存在账号封禁风险，只有 IP 级频控风险 → 调用之间自行 sleep、勿并发。
- 默认受 Airbnb robots.txt 拦截；本客户端显式加 --ignore-robots-txt 才能取数，
  仅用于个人行程比价的低频查询，禁止批量商用抓取。
- 首次运行 npx 会下载包，需要 node>=18（本机已具备）。
"""
import argparse, json, os, queue, subprocess, sys, threading, time


class AirbnbMCP:
    def __init__(self, timeout=90):
        self.proc = subprocess.Popen(
            ["npx", "-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, bufsize=1, env=dict(os.environ))
        self.q = queue.Queue()
        threading.Thread(target=self._reader, daemon=True).start()
        self.i = 0
        self._init(timeout)

    def _reader(self):
        for line in self.proc.stdout:
            self.q.put(line)

    def _send(self, obj):
        self.proc.stdin.write(json.dumps(obj) + "\n"); self.proc.stdin.flush()

    def _wait(self, rid, timeout):
        end = time.time() + timeout
        while time.time() < end:
            try:
                msg = json.loads(self.q.get(timeout=5))
            except queue.Empty:
                continue
            if msg.get("id") == rid:
                return msg
        raise TimeoutError("MCP 响应超时")

    def _init(self, timeout):
        self.i += 1
        self._send({"jsonrpc": "2.0", "id": self.i, "method": "initialize", "params": {
            "protocolVersion": "2024-11-05", "capabilities": {},
            "clientInfo": {"name": "travel-books", "version": "1"}}})
        self._wait(self.i, timeout)
        self._send({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def call(self, name, args, timeout=90):
        self.i += 1; rid = self.i
        self._send({"jsonrpc": "2.0", "id": rid, "method": "tools/call",
                    "params": {"name": name, "arguments": args}})
        msg = self._wait(rid, timeout)
        if "error" in msg:
            raise RuntimeError(msg["error"])
        txt = msg["result"]["content"][0]["text"]
        try:
            return json.loads(txt)
        except json.JSONDecodeError:
            return {"raw": txt}

    def close(self):
        try: self.proc.terminate()
        except Exception: pass


def brief(item):
    sc = item.get("structuredContent", {}) or {}
    dp = (item.get("structuredDisplayPrice", {}) or {}).get("primaryLine", {}) or {}
    name = (((item.get("demandStayListing", {}) or {}).get("description", {}) or {})
            .get("name", {}) or {}).get("localizedStringWithTranslationPreference", "?")
    coord = (((item.get("demandStayListing", {}) or {}).get("location", {}) or {})
             .get("coordinate", {}) or {})
    return {"id": item.get("id"), "name": name,
            "beds": sc.get("primaryLine"),
            "rating": item.get("avgRatingA11yLabel"),
            "badges": item.get("badges"),
            "price": dp.get("accessibilityLabel"),
            "lat": coord.get("latitude"), "lng": coord.get("longitude"),
            "url": item.get("url")}


def cmd_search(a):
    c = AirbnbMCP()
    try:
        data = c.call("airbnb_search", {
            "location": a.query, "checkin": a.arrival, "checkout": a.departure,
            "adults": a.adults, "limit": a.limit})
    finally:
        c.close()
    results = data.get("searchResults", []) if isinstance(data, dict) else []
    rows = [brief(x) for x in results]
    if a.out:
        json.dump({"raw": data, "brief": rows}, open(a.out, "w"),
                  ensure_ascii=False, indent=1)
    print(f"# {a.query} {a.arrival}~{a.departure} 共 {len(rows)} 条")
    for r in rows:
        print("- {name} | {price} | {rating} | {beds}".format(**r))
    if a.out: print("saved:", a.out)


def cmd_details(a):
    c = AirbnbMCP()
    try:
        data = c.call("airbnb_listing_details", {
            "id": a.listing_id, "checkin": a.arrival, "checkout": a.departure,
            "adults": a.adults})
    finally:
        c.close()
    if a.out:
        json.dump(data, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(json.dumps(data, ensure_ascii=False)[:3000])
    if a.out: print("saved:", a.out)


def cmd_batch(a):
    """单会话内串行多个检索，请求间长 sleep，降低软限流概率。
    jobs 文件格式: [{"name":"almaty","query":"...","arrival":"...","departure":"..."}]"""
    jobs = json.load(open(a.jobs))
    c = AirbnbMCP()
    out = {}
    if a.warmup:
        print(f"warmup {a.warmup}s ...", flush=True); time.sleep(a.warmup)
    try:
        for idx, j in enumerate(jobs):
            if idx:
                time.sleep(a.gap)
            data = None; results = []
            for attempt in range(a.retry + 1):
                try:
                    data = c.call("airbnb_search", {
                        "location": j["query"], "checkin": j["arrival"],
                        "checkout": j["departure"], "adults": j.get("adults", 2),
                        "limit": j.get("limit", 20)})
                except Exception as e:
                    data = {"error": str(e)}
                results = data.get("searchResults", []) if isinstance(data, dict) else []
                if results or attempt == a.retry:
                    break
                print(f"  {j['name']} 第{attempt+1}次空结果，{a.gap}s 后同会话重试", flush=True)
                time.sleep(a.gap)
            rows = [brief(x) for x in results]
            out[j["name"]] = {"query": j, "brief": rows, "raw": data}
            print(f"# {j['name']}: {len(rows)} 条", flush=True)
            for r in rows[:8]:
                print("  -", r["name"], "|", r["price"], "|", r["rating"])
    finally:
        c.close()
    json.dump(out, open(a.out, "w"), ensure_ascii=False, indent=1)
    print("saved:", a.out)


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query"); s.add_argument("arrival"); s.add_argument("departure")
    s.add_argument("--adults", type=int, default=2)
    s.add_argument("--limit", type=int, default=30); s.add_argument("--out")
    s.set_defaults(fn=cmd_search)
    d = sub.add_parser("details")
    d.add_argument("listing_id"); d.add_argument("arrival"); d.add_argument("departure")
    d.add_argument("--adults", type=int, default=2); d.add_argument("--out")
    d.set_defaults(fn=cmd_details)
    b = sub.add_parser("batch")
    b.add_argument("jobs"); b.add_argument("out")
    b.add_argument("--gap", type=int, default=20)
    b.add_argument("--warmup", type=int, default=0)
    b.add_argument("--retry", type=int, default=2)
    b.set_defaults(fn=cmd_batch)
    a = p.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
