#!/usr/bin/env python3
"""Trivago 官方远程 MCP 客户端（免 key、免登录的官方授权通道）。

用法:
  python3 trivago_mcp_client.py search "Almaty, Kazakhstan" 2026-10-02 2026-10-03 \
      [--adults 2] [--rooms 1] [--currency CNY] [--lang ZH_HANS_CN] [--out a.json]
  python3 trivago_mcp_client.py trends "Almaty" 2026-10 [--currency CNY]
  python3 trivago_mcp_client.py tools   # 列出全部工具与 schema

输出: 标准输出打印摘要；--out 保存原始 JSON。
注意: country 只影响展示市场（无 KZ 选项时用 HK/US 即可），库存按 query 全球检索。
"""
import argparse, json, sys, urllib.request

URL = "https://mcp.trivago.com/mcp"


class TrivagoMCP:
    def __init__(self):
        self.sid = None
        self.i = 0
        self._init()

    def _call(self, method, params=None, notification=False, timeout=90):
        self.i += 1
        body = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            body["params"] = params
        if not notification:
            body["id"] = self.i
        req = urllib.request.Request(
            URL, data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json",
                     "Accept": "application/json, text/event-stream"})
        if self.sid:
            req.add_header("Mcp-Session-Id", self.sid)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            if r.headers.get("Mcp-Session-Id"):
                self.sid = r.headers["Mcp-Session-Id"]
            raw = r.read().decode()
        if raw.startswith("event:"):  # SSE 包裹
            for line in raw.splitlines():
                if line.startswith("data:"):
                    raw = line[5:].strip()
        return None if notification else json.loads(raw)

    def _init(self):
        self._call("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                  "clientInfo": {"name": "travel-books", "version": "1"}})
        self._call("notifications/initialized", {}, notification=True)

    def tools_list(self):
        return self._call("tools/list")["result"]["tools"]

    def call_tool(self, name, args, timeout=120):
        res = self._call("tools/call", {"name": name, "arguments": args}, timeout=timeout)
        if "error" in res:
            raise RuntimeError(res["error"])
        txt = res["result"]["content"][0]["text"]
        return txt

    @staticmethod
    def parse_output(txt):
        """search 工具返回文本里嵌了 {"output": "[...json str...]"}，解析成 list。"""
        s = txt.find("{")
        obj = json.loads(txt[s:])
        if "output" in obj:
            return json.loads(obj["output"])
        return obj


def cmd_search(a):
    c = TrivagoMCP()
    txt = c.call_tool("trivago-accommodation-search", {
        "query": a.query, "arrival": a.arrival, "departure": a.departure,
        "adults": a.adults, "rooms": a.rooms,
        "currency": a.currency, "language": a.lang,
        "country": a.country})
    items = c.parse_output(txt)
    if a.out:
        json.dump(items, open(a.out, "w"), ensure_ascii=False, indent=1)
    print(f"# {a.query} {a.arrival}~{a.departure} 共 {len(items)} 条 ({a.currency})")
    for h in items:
        print("- {name} | {price} | {adv} | 评级{hr}/评{rr}({rc})".format(
            name=h.get("accommodation_name"), price=h.get("price_per_night"),
            adv=h.get("advertisers"), hr=h.get("hotel_rating"),
            rr=h.get("review_rating"), rc=h.get("review_count")))
    if a.out:
        print("saved:", a.out)


def cmd_trends(a):
    c = TrivagoMCP()
    txt = c.call_tool("trivago-destination-price-trends", {
        "destination": a.query, "month": a.month, "currency": a.currency})
    print(txt[:4000])
    if a.out:
        open(a.out, "w").write(txt)


def cmd_tools(a):
    c = TrivagoMCP()
    for t in c.tools_list():
        print("==", t["name"])
        print("  ", t.get("description", "").strip()[:200])
        print("  args:", list(t.get("inputSchema", {}).get("properties", {}).keys()))


def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("search")
    s.add_argument("query"); s.add_argument("arrival"); s.add_argument("departure")
    s.add_argument("--adults", type=int, default=2)
    s.add_argument("--rooms", type=int, default=1)
    s.add_argument("--currency", default="CNY")
    s.add_argument("--lang", default="ZH_HANS_CN")
    s.add_argument("--country", default="HK")
    s.add_argument("--out")
    s.set_defaults(fn=cmd_search)
    t = sub.add_parser("trends")
    t.add_argument("query"); t.add_argument("month")
    t.add_argument("--currency", default="CNY"); t.add_argument("--out")
    t.set_defaults(fn=cmd_trends)
    tl = sub.add_parser("tools"); tl.set_defaults(fn=cmd_tools)
    a = p.parse_args(); a.fn(a)


if __name__ == "__main__":
    main()
