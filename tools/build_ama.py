import os
from PIL import Image
ROOT="/Users/bytedance/workspace/travel-books"
RAW=os.path.join(ROOT,"raw/xhs/imgs2/museum_ama")
OUT=os.path.join(ROOT,"assets/gallery2/museum_ama")
os.makedirs(OUT,exist_ok=True)
# (noteid, rawfile, caption, like)
SEL=[
 ("6a93b83e0000000007004c40","v07.webp","馆外广场与石灰岩+铝板几何立面（Chapman Taylor 设计）","13"),
 ("69d14636","n01.webp","棱角分明的侏罗纪石灰岩入口立面","60"),
 ("6a93037c000000000303c3f7","s04.webp","馆前倒影水池与彩色小丑雕塑","13"),
 ("68e1ea45000000000700acc0","q10.webp","玻璃天光下的石材中庭与大楼梯","25"),
 ("6a37a9b400000000220147eb","t10.webp","石灰岩块体交错的室内几何空间","10"),
 ("69d14636","n02.webp","理查德·塞拉弧形耐候钢钢板装置","60"),
 ("69d14636","n11.webp","安塞姆·基弗巨幅综合材料画作","60"),
 ("69d14636","n13.webp","比尔·维奥拉暗光影像厅","60"),
 ("69d14636","n06.webp","哈萨克游牧主题油画·围坐聚餐","60"),
 ("6a37a9b400000000220147eb","t13.webp","本土陶塑面具与头像雕塑墙","10"),
 ("6a6831eb000000000f01e5b5","p08.webp","哈萨克传统纹样长袍织物艺术","20"),
 ("6a93037c000000000303c3f7","s15.webp","草间弥生 LOVE IS CALLING 无限镜屋","13"),
 ("68e1ea45000000000700acc0","q08.webp","色彩分区的现当代绘画展厅","25"),
 ("69a79c41000000002801c87a","m01.webp","出口处文创咖啡区·苹果茶","51"),
]
def save(im,path,edge,q):
    im=im.convert("RGB");w,h=im.size;s=edge/max(w,h)
    if s<1:im=im.resize((round(w*s),round(h*s)),Image.LANCZOS)
    im.save(path,"WEBP",quality=q,method=6)
items=[]
for i,(nid,rf,cap,like) in enumerate(SEL,1):
    src=os.path.join(RAW,nid,rf);im=Image.open(src)
    full=os.path.join(OUT,f"museum_ama_{i:02d}.webp");th=os.path.join(OUT,f"museum_ama_{i:02d}.th.webp")
    save(im,full,1280,70);save(Image.open(src),th,480,62)
    url=f"https://www.xiaohongshu.com/explore/{nid}"
    items.append((f"assets/gallery2/museum_ama/museum_ama_{i:02d}.webp",cap,url,like))
    print(i,rf,os.path.getsize(full)//1024,"KB",os.path.getsize(th)//1024,"KB")
# 生成 JS 块
lines=['  "museum_ama": {title:"阿拉木图艺术博物馆 AMA", items:[']
for src,cap,url,like in items:
    lines.append(f'    {{"src": "{src}", "cap": "{cap}", "url": "{url}", "like": "{like}"}},')
lines.append('  ]},')
block="\n".join(lines)+"\n"
js=os.path.join(ROOT,"assets/gallery2/gallery-data.js")
s=open(js,encoding="utf-8").read()
if '"museum_ama"' not in s:
    idx=s.rstrip().rfind("};")
    s=s[:idx]+block+s[idx:]
    open(js,"w",encoding="utf-8").write(s)
    print("JS inserted, items:",len(items))
else:
    print("museum_ama already present, skip insert")
