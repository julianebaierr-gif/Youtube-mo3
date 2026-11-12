from PIL import Image, ImageDraw
S=1024
def build(bg_radius=0.22):
    im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,S-1,S-1],radius=int(S*bg_radius),fill=(15,23,42,255))
    # big play triangle
    tri=[(S*0.27,S*0.16),(S*0.27,S*0.84),(S*0.88,S*0.50)]
    d.polygon(tri,fill=(225,29,72,255))
    # soften corners: draw circles at vertices? use thick line join
    d.line(tri+[tri[0]],fill=(225,29,72,255),width=int(S*0.06),joint="curve")
    for x,y in tri:
        r=S*0.03; d.ellipse([x-r,y-r,x+r,y+r],fill=(225,29,72,255))
    # white sound bars
    for cx,h in ((0.40,0.20),(0.50,0.36),(0.60,0.14)):
        w=S*0.045; x=S*cx; hh=S*h
        d.rounded_rectangle([x-w/2,S*0.5-hh/2,x+w/2,S*0.5+hh/2],radius=int(w/2),fill=(255,255,255,255))
    return im
im=build()
for folder in ("static","public"):
    for n,sz in (("icon-512.png",512),("icon-192.png",192),("favicon-96x96.png",96),("favicon-48x48.png",48)):
        if folder=="public" and n.startswith("favicon-"): continue
        im.resize((sz,sz),Image.LANCZOS).save(f"{folder}/{n}")
    im.resize((256,256),Image.LANCZOS).save(f"{folder}/favicon.ico",sizes=[(16,16),(32,32),(48,48),(64,64)])
svg='''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <rect width="512" height="512" rx="112" fill="#0f172a"/>
  <path d="M148 84 L148 428 L448 256 Z" fill="#e11d48" stroke="#e11d48" stroke-width="30" stroke-linejoin="round"/>
  <rect x="193" y="206" width="23" height="100" rx="11.5" fill="#ffffff"/>
  <rect x="245" y="164" width="23" height="184" rx="11.5" fill="#ffffff"/>
  <rect x="297" y="220" width="23" height="72" rx="11.5" fill="#ffffff"/>
</svg>
'''
for p in ("static/favicon.svg","public/favicon.svg"):
    open(p,"w",newline="\n").write(svg)
# patch FAVICON_SVG_CONTENT in main.py
import re
s=open("app/main.py",encoding="utf-8").read()
s2=re.sub(r'FAVICON_SVG_CONTENT = """.*?"""', lambda m:'FAVICON_SVG_CONTENT = """'+svg+'"""', s, count=1, flags=re.S)
open("app/main.py","w",encoding="utf-8",newline="").write(s2)
print("ok", s!=s2)
