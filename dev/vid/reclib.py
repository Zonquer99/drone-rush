import asyncio, os, shutil, subprocess
from playwright.async_api import async_playwright

W, H, DSF = 405, 720, 1080/405
FPS = 30

AP_JS = r"""
window.__hits=0;
window.__realCollides=collides;
collides=function(o){if(window.__realCollides(o)){window.__hits++;} return window.__god?false:window.__realCollides(o)};
window.__apTarget=300;
window.__ap=function(){
  if(state!=='play'){holding=false;return}
  let tgt=window.__cruise||300, best=null, bd=1e9;
  for(const o of obs){
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
  window.__apTarget=tgt;
  const pred=drone.y+drone.vy*0.16;
  holding=pred>tgt;
};
window.__tick=function(dt){window.__ap();update(dt)};
window.__render=function(){draw();hud();
  const show=state==='play'&&!!SK.phase&&!$('hud').hidden;const b=$('phBtn');b.hidden=!show;if(show){$('phN').textContent='×'+phases;b.classList.toggle('on',phaseT>0)}};
"""

OVL_CSS = """
#ovl{position:fixed;left:0;right:0;top:63%;z-index:50;text-align:center;pointer-events:none;padding:0 18px;transition:none}
#ovl .t{display:inline-block;font-family:var(--display),system-ui;font-weight:800;font-size:31px;line-height:1.15;color:#fff;
  background:rgba(10,6,24,.72);padding:10px 16px;border-radius:16px;box-shadow:0 6px 24px rgba(0,0,0,.45);border:2px solid rgba(255,211,90,.55)}
#ovl .s{display:block;margin-top:8px;font-family:system-ui;font-weight:700;font-size:17px;color:#ffd35a;text-shadow:0 2px 6px #000}
#endc{position:fixed;inset:0;z-index:60;display:none;flex-direction:column;align-items:center;justify-content:center;gap:16px;
  background:radial-gradient(circle at 50% 40%,rgba(80,40,140,.92),rgba(8,5,20,.97));text-align:center;padding:24px}
#endc h1{font-family:var(--display),system-ui;font-size:44px;line-height:1;margin:0;color:#fff}
#endc h1 span{color:#ffb35a}
#endc p{margin:0;font-family:system-ui;font-weight:700;color:#e8e0ff;font-size:20px}
#endc .tg{margin-top:6px;display:inline-flex;align-items:center;gap:10px;background:#2aa3e0;color:#fff;font-family:system-ui;font-weight:800;font-size:24px;padding:14px 22px;border-radius:18px;box-shadow:0 8px 30px rgba(42,163,224,.5)}
#endc .tg i{font-style:normal;font-size:26px}
#endc small{font-family:system-ui;color:#bdb3e6;font-size:16px}
"""

class Rec:
    def __init__(self, name):
        self.name = name
        self.dir = f'/tmp/claude-0/s/vid/frames_{name}'
        shutil.rmtree(self.dir, ignore_errors=True); os.makedirs(self.dir)
        self.n = 0

    async def start(self, p, lang='es'):
        self.b = await p.chromium.launch()
        ctx = await self.b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=DSF, locale='es-ES')
        self.pg = pg = await ctx.new_page()
        self.errs = []
        pg.on('pageerror', lambda e: self.errs.append(str(e)))
        for u in ['**/supabase.min.js', '**/telegram.org/**', '**/libtl.com/**']:
            await pg.route(u, lambda r: r.fulfill(body='', content_type='text/javascript'))
        await pg.goto('file:///tmp/claude-0/s/vid/rec.html'); await pg.wait_for_timeout(400)
        await pg.evaluate("l=>localStorage.setItem('dronerush.v1',JSON.stringify({gen:2,named:true,pilot:'Zonquer',lang:l,sound:false,music:false,games:30,uG:30,uB:4000,best:4000,unl:['shop','free','mis','pass','inv','adv','pvp'],unlNew:[]}))", lang)
        await pg.reload(); await pg.wait_for_timeout(700)
        await pg.add_style_tag(content=OVL_CSS)
        await pg.evaluate("""()=>{const o=document.createElement('div');o.id='ovl';document.body.append(o);
          const e=document.createElement('div');e.id='endc';document.body.append(e);}""")
        await pg.evaluate("c=>__t(c)", AP_JS)
        await pg.evaluate("__t('window.__manual=true')")
        await pg.wait_for_timeout(100)

    async def js(self, code):
        return await self.pg.evaluate("c=>__t(c)", code)

    async def pos(self, top):
        await self.pg.evaluate("t=>document.getElementById('ovl').style.top=t", top)

    async def text(self, t, sub=''):
        await self.pg.evaluate("([t,s])=>{const o=document.getElementById('ovl');o.innerHTML=t?`<span class=t>${t}</span>`+(s?`<span class=s>${s}</span>`:''):''}", [t, sub])

    async def endcard(self, show=True, lang='es'):
        html = ("<h1>DRONE<br><span>RUSH</span></h1><p>Juega gratis en Telegram</p><div class=tg><i>✈</i>@dronerushhbot</div><small>Sin descargar nada · PvP · Torneos · Skins</small>"
                if lang == 'es' else
                "<h1>DRONE<br><span>RUSH</span></h1><p>Play free on Telegram</p><div class=tg><i>✈</i>@dronerushhbot</div><small>No download · PvP · Tournaments · Skins</small>")
        await self.pg.evaluate("([s,h])=>{const e=document.getElementById('endc');e.innerHTML=h;e.style.display=s?'flex':'none'}", [show, html])

    async def shot(self):
        await self.js('__render()')
        await self.pg.screenshot(path=f'{self.dir}/f{self.n:05d}.jpg', type='jpeg', quality=88)
        self.n += 1

    async def run(self, seconds, speed=1.0, every=None):
        frames = int(seconds * FPS)
        sub = max(1, int(round(2 * speed)))
        dt = (1 / FPS) * speed / sub
        for i in range(frames):
            await self.js(f'for(let i=0;i<{sub};i++)__tick({dt})')
            if every: await every(i)
            await self.shot()

    async def hold(self, seconds):
        for i in range(int(seconds * FPS)):
            await self.shot()

    async def finish(self, out):
        await self.b.close()
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{self.dir}/f%05d.jpg',
                        '-vf', 'scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                        '-movflags', '+faststart', out], check=True)
        return out
