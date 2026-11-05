from reclib import *

EPIC_CSS = """
#ovl{top:58%!important}
#ovl .t{font-size:40px!important;background:none!important;border:none!important;box-shadow:none!important;padding:0 10px!important;
  color:#fff;-webkit-text-stroke:2px rgba(20,8,40,.9);paint-order:stroke fill;
  text-shadow:0 0 18px var(--gc,#ff4fd8),0 0 36px var(--gc,#ff4fd8),0 6px 0 rgba(0,0,0,.6)!important;letter-spacing:1px}
#ovl .s{font-size:21px!important;color:#ffe680!important;text-shadow:0 2px 8px #000,0 0 12px rgba(0,0,0,.8)!important}
#ovl .rk{display:block;font-family:var(--display),system-ui;font-weight:900;font-size:86px;line-height:1;color:#ffd35a;-webkit-text-stroke:3px #2a1200;paint-order:stroke fill;text-shadow:0 0 30px #ffb000,0 8px 0 rgba(0,0,0,.6);margin-bottom:6px}
#fl{position:fixed;inset:0;z-index:55;background:#fff;opacity:0;pointer-events:none}
#vig{position:fixed;inset:0;z-index:54;pointer-events:none;background:radial-gradient(ellipse at 50% 50%,rgba(0,0,0,0) 55%,rgba(0,0,0,.45) 100%)}
#bar{position:fixed;left:0;right:0;height:0;background:#000;z-index:56}
"""

AP2 = r"""
window.__ap=function(){
  if(state!=='play'){holding=false;return}
  let tgt=window.__cruise||300, best=null, bd=1e9;
  const through=(ghostT>0)||window.__through;
  // portals first
  let pq=null,pd=1e9;for(const q of portals){const d=q.x-drone.x;if(d>-10&&d<pd){pd=d;pq=q}}
  if(pq&&pd<520){tgt=pq.y}
  else if(!through){
    for(const o of obs){
      if(o.suck)continue;
      const right=o.type==='pylon'?o.x+o.w+20:o.type==='turbine'?o.x+o.L+20:o.x+60;
      if(right<drone.x-10)continue;
      const d=(o.type==='turbine'?o.x-o.L:o.x)-drone.x; if(d>430)continue;
      if(d<bd){bd=d;best=o}
    }
    if(best){
      if(best.type==='pylon')tgt=(best.top+best.bot)/2;
      else if(best.type==='turbine')tgt=Math.max(46,best.hub-best.L-34);
      else{const y0=best.y0; tgt=y0>GY*0.5?Math.max(60,y0-150):Math.min(GY-90,y0+150)}
    }
  }
  window.__apTarget=tgt;
  holding=drone.y+drone.vy*0.16>tgt;
};
"""

class Rec2(Rec):
    async def start(self, p, lang='es'):
        await super().start(p, lang)
        await self.pg.add_style_tag(content=EPIC_CSS)
        await self.pg.evaluate("""()=>{for(const id of ['fl','vig']){const d=document.createElement('div');d.id=id;document.body.append(d)}}""")
        await self.js(AP2)
        self.pop = 99; self.zoom = 0.0; self.flash = 0.0; self.speed = 1.0

    async def text(self, t, sub='', rank='', color='#ff4fd8'):
        await self.pg.evaluate("([t,s,r,c])=>{const o=document.getElementById('ovl');o.style.setProperty('--gc',c);o.innerHTML=t?(r?`<span class=rk>${r}</span>`:'')+`<span class=t>${t}</span>`+(s?`<span class=s>${s}</span>`:''):''}", [t, sub, rank, color])
        self.pop = 0

    def punch(self, z=0.12, f=0.75):
        self.zoom = max(self.zoom, z); self.flash = max(self.flash, f)

    async def shot(self):
        p = self.pop; sc = 1 + 0.45 * (2.718 ** (-p / 2.2)) if p < 30 else 1
        op = min(1, p / 2 + 0.3)
        await self.pg.evaluate("([sc,op,z,f])=>{const o=document.getElementById('ovl');o.style.transform=`scale(${sc})`;o.style.opacity=op;"
                               "document.getElementById('wrap').style.transform=`scale(${1+z})`;document.getElementById('fl').style.opacity=f}",
                               [sc, op, self.zoom, self.flash])
        self.pop += 1; self.zoom *= 0.86; self.flash *= 0.72
        if self.zoom < 0.002: self.zoom = 0
        if self.flash < 0.01: self.flash = 0
        await super().shot()

    async def play(self, seconds, speed=1.0, every=None):
        frames = int(seconds * FPS)
        for i in range(frames):
            sp = self.speed * speed
            sub = max(1, int(round(2 * sp)))
            dt = (1 / FPS) * sp / sub
            await self.js(f'for(let i=0;i<{sub};i++){{__tick({dt});battery=Math.max(battery,60)}}')
            if every: await every(i)
            await self.shot()
