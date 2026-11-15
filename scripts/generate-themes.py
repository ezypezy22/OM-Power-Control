"""Generate the theme blocks in live.html from the dark palette in :root.

Dark is the source of truth. Every colour token is named <kind>-<family><lightness>: bg surface, tx text,
ln line, fl meter fill, sh shadow or scrim. The other themes are derived per kind, then text tokens are
pushed until they meet the contrast target on that theme's surfaces. Run it after changing a dark value;
it rewrites the block between the THEMES markers and prints a contrast report (exit 1 if a target fails).

  python3 scripts/generate-themes.py [--check]
"""
import colorsys,re,sys
from pathlib import Path
PAGE=Path(__file__).resolve().parent.parent/'live.html'
START,END='/*THEMES:START*/','/*THEMES:END*/'
THEMES=('light','hc-dark','hc-light','cb')   # dark is the default :root
def parse(h):
 h=h[1:]
 if len(h)in(3,4):h=''.join(c*2 for c in h)
 r,g,b=(int(h[i:i+2],16)/255 for i in(0,2,4));a=int(h[6:8],16)/255 if len(h)==8 else 1
 hh,l,s=colorsys.rgb_to_hls(r,g,b);return hh*360,l,s,a
def fmt(h,l,s,a=1):
 l=min(1,max(0,l));s=min(1,max(0,s));r,g,b=colorsys.hls_to_rgb((h%360)/360,l,s)
 x='#%02x%02x%02x'%(round(r*255),round(g*255),round(b*255))
 return x+('%02x'%round(a*255) if a<.999 else '')
def lum(hexc):
 h,l,s,_=parse(hexc);r,g,b=colorsys.hls_to_rgb(h/360,l,s)
 f=lambda c:c/12.92 if c<=.03928 else((c+.055)/1.055)**2.4
 return .2126*f(r)+.7152*f(g)+.0722*f(b)
def ratio(a,b):
 x,y=sorted((lum(a),lum(b)),reverse=True);return(x+.05)/(y+.05)
def fam(h,l,s):
 if s<.15 or l<.04:return 'n'
 if h<20 or h>=330:return 'r'
 if h<75:return 'a'
 if h<190:return 'g'
 return 'b'

# Named tokens and the surfaces every theme is checked against.
NAMED={
 'bg':   {'light':'#eef2f4','hc-dark':'#000000','hc-light':'#ffffff'},
 'card': {'light':'#ffffff','hc-dark':'#000000','hc-light':'#ffffff'},
 'line': {'light':'#b9c6cc','hc-dark':'#c9d4d8','hc-light':'#1a2328'},
 'text': {'light':'#121c22','hc-dark':'#ffffff','hc-light':'#000000'},
 'muted':{'light':'#43545c','hc-dark':'#e3eaec','hc-light':'#1a2328'},
 'amber':{'light':'#8a5200','hc-dark':'#ffd37a','hc-light':'#6b3d00'},
 'green':{'light':'#0b6b4c','hc-dark':'#7ff0c4','hc-light':'#00513a'},
 'bad':  {'light':'#b3261e','hc-dark':'#ff9a8f','hc-light':'#8f1d15'},
}
SURFACE={'light':('bg','card'),'hc-dark':('bg','card'),'hc-light':('bg','card')}
TARGET={'light':4.5,'hc-dark':7.0,'hc-light':7.0,'cb':4.5}
CB_HUE={'g':196,'r':326,'a':48}   # colour-blind safe: green becomes blue, red/orange becomes magenta, amber stays yellow
def cb_hue(h,f):
 if f=='g':return CB_HUE['g']
 if f=='r':return CB_HUE['r']
 if f=='a' and h<30:return 335     # orange sits with red, apart from yellow
 return h
def derive(name,dark,theme):
 h,l,s,a=parse(dark);kind,rest=name.split('-',1);f=fam(h,l,s)
 if theme=='cb':
  if f in('g','r') or(f=='a' and h<30):h=cb_hue(h,f)
  if f=='b':s*=.55            # info blue stays quiet so it is not read as the new "good" colour
  return fmt(h,l,s,a)
 light=theme in('light','hc-light');hc=theme.startswith('hc')
 if kind=='sh':return fmt(h,l,s,min(1,a*(.45 if light else 1.3 if hc else 1)))
 if f=='n':s=min(s,.14)
 if kind=='tx':
  nl=1-l if light else l
  if hc and not light:nl=max(l,.82)
  if hc and light:nl=min(nl,.2)
  return fmt(h,nl,min(1,s*(1.1 if hc else 1)),a)        # contrast fix-up happens against the surface later
 if kind=='ln':
  if hc:return fmt(h,.18 if light else .78,min(s,.3),a)
  return fmt(h,1-l if light else l,s*(.7 if light else 1),a)
 if kind=='fl':   # meter fills sit on the track, so keep them mid-tone with strong saturation
  nl=min(l,.52) if light else l
  if hc:nl=.4 if light else max(l,.62)
  return fmt(h,nl,max(s,.62),a)
 # bg
 if f=='n':
  nl=1-l if light else l
  if hc:nl=(1-(1-nl)*.08) if light else l*.15
  return fmt(h,nl,s,a)
 nl=1-l if light else l
 if hc:nl=.93 if light else min(l,.16)
 return fmt(h,nl,min(1,s*(.9 if light else 1.15 if hc else 1)),a)
def fixup(value,surfaces,target,theme):
 """Move a text colour along lightness until it meets the target ratio on every surface."""
 h,l,s,a=parse(value);light_surface=all(lum(x)>.4 for x in surfaces);step=-.01 if light_surface else .01
 for _ in range(100):
  cur=fmt(h,l,s)
  if all(ratio(cur,x)>=target for x in surfaces):break
  l+=step
  if not(0<=l<=1):break
 return fmt(h,l,s,a)
def read(page):
 root=re.search(r':root\{([^}]*)\}',page).group(1)
 return dict(re.findall(r'--([\w-]+):(#[0-9a-fA-F]{3,8})',root))
def build(dark):
 tokens={k:v for k,v in dark.items() if re.match(r'(bg|tx|ln|fl|sh)-',k)}
 out={};report=[];failed=False
 for theme in THEMES:
  vals={}
  for k,v in tokens.items():vals[k]=derive(k,v,theme)
  for k,tbl in NAMED.items():
   vals[k]=tbl[theme] if theme in tbl else dark[k]
   if theme=='cb':vals[k]=dark[k]
  if theme=='cb':
   vals['green']='#5fc9ee';vals['amber']=dark['amber'];vals['bad']='#e86fb5';vals['bad']='#e86fb5'
  light=theme in('light','hc-light')
  base='light' if light else 'dark'
  # surfaces text must clear: page, card and every bg token a text can sit on
  surf=[vals['bg'],vals['card']]+[v for k,v in vals.items() if k.startswith('bg-') and parse(v)[3]==1]
  surf=[x for x in surf if (lum(x)>.5 if light else lum(x)<.12)] or [vals['bg']]   # mid-tone bg tokens are meter tracks, never text surfaces
  for k in [k for k in vals if k.startswith('tx-')]+['text','muted','amber','green','bad']:
   vals[k]=fixup(vals[k],surf,TARGET[theme],theme)
   worst=min(ratio(vals[k],x) for x in surf)
   report.append((theme,k,round(worst,2)))
   if worst<TARGET[theme]-.05:failed=True
  out[theme]=vals
 return out,report,failed
def block(out):
 lines=[START]
 for theme,vals in out.items():
  scheme='light' if theme in('light','hc-light') else 'dark'
  lines.append('[data-theme=%s]{color-scheme:%s;%s}'%(theme,scheme,';'.join('--%s:%s'%(k,v) for k,v in vals.items())))
 lines.append(END);return '\n'.join(lines)
def main():
 page=PAGE.read_text(encoding='utf-8');dark=read(page)
 out,report,failed=build(dark)
 if START in page:page=re.sub(re.escape(START)+r'.*?'+re.escape(END),lambda m:block(out),page,flags=re.S)
 else:page=page.replace('</style><main>',block(out)+'\n</style><main>',1)
 if '--check' not in sys.argv:PAGE.write_text(page,encoding='utf-8')
 low=[r for r in report if r[2]<TARGET[r[0]]-.05]
 print('themes:',', '.join(THEMES),'| text tokens checked:',len(report),'| below target:',len(low))
 for r in low:print('  LOW',r)
 sys.exit(1 if failed else 0)
if __name__=='__main__':main()
