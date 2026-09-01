# -*- coding: utf-8 -*-
"""把小红书口碑层（xhs_reputation + assets/lodge-xhs 过审图）回填进住宿选型.html 的 SEED。
只做幂等的定点替换：1) 给既有卡补 xhs 文本与实拍；2) 在 ab12 后插入新卡。"""
import re, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ROOT = os.path.join(ROOT, "trips", "2026-10-哈萨克斯坦-阿拉木图阿克套")
HTML = os.path.join(ROOT, "住宿选型.html")
LX = "assets/lodge-xhs"

def jsstr(s):
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"

def imgs_of(d):
    p = os.path.join(ROOT, LX, d)
    return sorted(f for f in os.listdir(p) if f.endswith(".webp"))

def img_entries(d, author, note_url, caps=None):
    out = []
    for f in imgs_of(d):
        cap = f"小红书实拍（{author}，AI双审强关联）"
        out.append("{src:%s,cap:%s,url:%s}" % (jsstr(f"{LX}/{d}/{f}"), jsstr(cap), jsstr(note_url)))
    return out

s = open(HTML, encoding="utf-8").read()

# ---------- 1) 既有卡：xhs 文本 + 实拍注入 ----------
def card_span(src, cid):
    i = src.index(f"id:'{cid}'")
    # 卡对象起点回退到 '{'
    start = src.rfind("{", 0, i)
    # 终点：下一个 "\n {id:'" 或 SEED 结束
    m = re.search(r"\n\s*\{id:'", src[i:])
    end = i + m.start() if m else src.index("];", i)
    return start, end

def enrich(src, cid, xhs_text, img_dir=None, author="", note_url=""):
    st, en = card_span(src, cid)
    card = src[st:en]
    # xhs 字段替换
    card2 = re.sub(r"xhs:'(?:[^'\\]|\\.)*'", "xhs:" + jsstr(xhs_text), card, count=1)
    # 实拍注入 imgs:[ ... ]（在 ],nights 前追加）
    if img_dir:
        entries = img_entries(img_dir, author, note_url)
        add = "\n   " + ",\n   ".join(entries)
        card2 = re.sub(r"(imgs:\[.*?)(\],\s*nights)",
                       lambda m: m.group(1) + ("" if m.group(1).rstrip().endswith((",", "[")) else ",") + add + m.group(2),
                       card2, count=1, flags=re.S)
    return src[:st] + card2 + src[en:]

H = {
 "h1": ("【1帖/30赞】2025新开业，步行到潘菲洛夫/升天大教堂/绿巴扎；自助早餐丰富、英语前台、含桑拿泳池；评论：大床房可摊两个大行李箱、无装修味、约600+/晚。几乎无差评。",
        "h1", "半拍", "https://www.xiaohongshu.com/explore/68e6797c0000000005013355"),
 "h3": ("【1帖/5赞】这是全服务Holiday Inn（非智选Express，勿订混）：约800+/晚、约20㎡、无瓶装水用楼层饮水机；评论冬季约400+、早餐牛肉好吃。小红书专属实拍极少，不拿Express图冒充。",
        None, "", ""),
 "h10":("【1帖/14赞】原万丽已摘牌。位置第一梯队（步行3-5分到里海、10分内永恒之火广场、近网红餐厅）；房间偏小偏旧、备品敷衍布草一般；英文好、room service好吃偏贵；OTA新客约300/晚。评论：阿特劳万丽或同摘牌。",
        "h10", "小羊削他", "https://www.xiaohongshu.com/explore/692bfb60000000001b025994"),
 "h13":("【2帖/326+42赞】1977苏联地标（旧5000坚戈图案），约2010翻新。务必订‘高级房+高楼层mountain view（东北向最佳）’：已翻新且避开低层酒吧噪音，雪山城景绝佳，高级房约480-580含早；标准房老旧像老招待所、WiFi弱；25层为原VIP元首层。",
        "h13", "远苏老饕/Aubrey", "https://www.xiaohongshu.com/explore/6a61a91c000000000903657e"),
}
for cid,(txt,d,a,u) in H.items():
    s = enrich(s, cid, txt, d, a, u)

# ---------- 2) 新卡 ----------
def card(cid, city, name, area, tier, price, rating, nights, tags, pros, cons, note, imgdir=None, author="", url=""):
    imgs = ""
    if imgdir:
        imgs = "imgs:[\n   " + ",\n   ".join(
            "{src:%s,cap:%s,url:%s}" % (jsstr(f"{LX}/{imgdir}/{f}"),
                                        jsstr(f"小红书实拍（{author}，AI双审强关联）"), jsstr(url))
            for f in imgs_of(imgdir)) + "\n  ],"
    else:
        imgs = "imgs:[],"
    return (
      "\n {id:'%s',city:'%s',name:%s,en:'',area:%s,tier:'%s',refPrice:%s,rating:%s,xhsCnt:'',tags:%s,"
      "colleague:'',xhs:'',pros:%s,cons:%s,\n  %s nights:'%s',mcpDate:'2026-09-01',status:'candidate',note:%s}"
    ) % (cid, city, jsstr(name), jsstr(area), tier, price, rating, jsstr(tags), jsstr(pros), jsstr(cons),
         imgs, nights, jsstr(note))

new_cards = ",".join([
 card("h22","aktau","Miramar Apart & Hotel（小红书实测）","阿克套/一街之隔沙滩","中端",313,0,"D5-D6",
      "海景露台,公寓式,带厨房",
      "海景露台绝美\n一街之隔到沙滩\n约313/晚价格适中",
      "设施旧、多次无预警停水\n早餐少\n离城区15分钟车程\n员工多不会英语",
      "小红书跨城帖实测（无糖元气花98赞）；为海景露台妥协之选，停水风险需有预案",
      "h22","无糖元气花","https://www.xiaohongshu.com/explore/685fd9f4000000001c032c0d"),
 card("h23","almaty","Mildom Premium（小红书实测）","北2街区升天大教堂/南500m Abay歌剧院","经济",237,3.7,"D1-D2,D4,D7",
      "位置王者,低价,近歌剧院/绿巴扎",
      "位置极佳，景点餐饮500m内\n实测约237/晚（MCP报价约502）",
      "无电梯\n走廊如迷宫\n处处陈旧，行李重/介意老旧慎选",
      "小红书跨城帖实测（无糖元气花98赞）；注意与 h16 Hotel Uyut 不是同一家",
      None),
 card("x1","almaty","Urban Yurt（UY民宿·Arbat旁）","Arbat步行街步行3分钟/地铁10分","民宿",400,4.8,"D1-D2,D4,D7",
      "Booking可订,自助入住,楼层行李柜,中国胃友好",
      "457赞高口碑、有复购好评\nArbat步行3分，楼下麻辣烫/新疆菜/便利店\n全程自助入住（前一天发代码）、每层行李柜\n卫生间干净",
      "无电梯（行李重可提前要2楼房）",
      "小红书高赞民宿综合最推荐；约400+/晚，4楼最里间树景好",
      "bnb_uy","Deries","https://www.xiaohongshu.com/explore/68ddfb1e0000000005001a16"),
 card("x2","almaty","Evergreen Apart（含早老公寓民宿）","79路直达机场/小树林闹中取静","民宿",350,0,"D1-D2,D4,D7",
      "含西式早6选,厨房洗衣机,英文房东,晚到可接待",
      "连住6天口碑、350/晚两人含早\n79路直达机场，去景点公交打车方便\n老板英文极好、23点到也有人\n有厨房洗衣机、实际有空调",
      "无电梯\n双床仅0.8m偏窄",
      "小红书54赞；适合多日长住，携程可订、联系靠WhatsApp",
      "bnb_evergreen","素素","https://www.xiaohongshu.com/explore/6a30faa8000000000f031fea"),
 card("x3","almaty","插画艺术家公寓（Airbnb）","Отау住宅区/汽车站打车16分","民宿",137,0,"D1-D2,D4,D7",
      "Airbnb,雪山阳台,艺术装修,英文房东",
      "259赞；3晚819、人均约137/晚极致性价比\n可见雪山阳台、家具齐全、房东审美佳\n房东会英语、Airbnb自动翻译",
      "在Отау住宅区，去核心景点需打车/公交",
      "小红书259赞；Airbnb预订，预算敏感+喜欢本地住区者优选",
      "bnb_art","Xuan_nnon","https://www.xiaohongshu.com/explore/684c2d5b000000002001da2b"),
 card("x4","almaty","市中心前苏联老公寓（氛围型·未具名）","市中心/楼下开放式公园","民宿",300,0,"D1-D2,D4,D7",
      "苏式老楼,树景+雪山窗景,生活感",
      "296赞；约300出头/间\n阳台对参天大树+雪山、木地板、楼下公园，生活氛围浓",
      "老公寓木地板响、大概率无电梯\n未具名，需在平台按‘市中心+高评分+山景’自行筛选",
      "代表一类市中心苏式老公寓风格，作为选房风格参考",
      "bnb_oldapt","一只盆盆","https://www.xiaohongshu.com/explore/68da79f900000000130355fe"),
 card("x5","almaty","雪山+清真寺景观高层Airbnb","看得到雪山的主干道高层","民宿",449,0,"D1-D2,D4,D7",
      "Airbnb,高层视野,清真寺+雪山同框",
      "200赞；3天1348（约449/晚）\n高层同时见Nur-Astana清真寺与阿拉套雪山\n有Airbnb真实深链可查",
      "阿拉木图雪山景较普遍，不必为视野溢价太多",
      "深链 airbnb.cn/rooms/1408781920735082043；原帖AI参考图已剔除只留实拍",
      "bnb_view","未能写下的诗","https://www.xiaohongshu.com/explore/69aa52f8000000002202fe61"),
 card("x6","aktau","苏式里海海景私人公寓（Booking）","阳台直面里海","民宿",130,0,"D5-D6",
      "Booking,私人房东,海景阳台,带洗衣机",
      "60赞；约130/晚\n阳台直面里海、房内三星洗衣机可洗衣、房东友善",
      "私人房东，支付方式需提前确认\n旺季易订满需早订、苏式老公寓楼龄",
      "小红书60赞；阿克套高性价比海景公寓代表",
      "bnb_aktau_sea","徐汇区柴静","https://www.xiaohongshu.com/explore/666155d2000000000e033839"),
])

anchor = "39条评论'}"
ai = s.index(anchor) + len(anchor)
assert s[ai:ai+2] == "];", "ab12 锚点后不是 ];，终止定位失败"
s = s[:ai] + "," + new_cards + s[ai:]  # ab12 末尾 } 后、]; 前插入 ,新卡

open(HTML, "w", encoding="utf-8").write(s)
print("backfill done; new length lines:", s.count("\n")+1)
