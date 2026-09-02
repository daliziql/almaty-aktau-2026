import os,sys
from PIL import Image,ImageDraw,ImageFont
ROOT="/Users/bytedance/workspace/travel-books/raw/xhs/imgs2/museum_ama"
CELL,PAD,COLS=300,26,5
try: F=ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf",16)
except: F=ImageFont.load_default()
for note in sorted(os.listdir(ROOT)):
    d=os.path.join(ROOT,note)
    if not os.path.isdir(d):continue
    fs=sorted(f for f in os.listdir(d) if f.endswith(".webp"))
    if not fs:continue
    rows=(len(fs)+COLS-1)//COLS
    W=COLS*(CELL+8)+16;H=rows*(CELL+PAD)+16
    sheet=Image.new("RGB",(W,H),"white");dr=ImageDraw.Draw(sheet)
    for i,f in enumerate(fs):
        try:im=Image.open(os.path.join(d,f)).convert("RGB")
        except Exception as e:continue
        im.thumbnail((CELL,CELL))
        cx=8+(i%COLS)*(CELL+8);cy=8+(i//COLS)*(CELL+PAD)
        sheet.paste(im,(cx,cy));dr.text((cx,cy+CELL+4),f,fill="black",font=F)
    out=os.path.join(ROOT,f"_contact_{note}.jpg")
    sheet.save(out,quality=82);print(out,sheet.size)
