from reclib2 import *

class Rec3(Rec2):
    async def start(self, p, lang='es'):
        await super().start(p, lang)
        # sabotaje: piloto automático que deja caer el dron
        await self.js("window.__apOk=window.__ap;window.__ap=function(){if(window.__sab&&state==='play'){if(window.__sab==='hit'){let o=null;for(const q of obs)if(q.type==='pylon'&&q.x+q.w>drone.x-5&&(!o||q.x<o.x))o=q;if(o){const ty=o.top>140?o.top-70:o.bot+70;holding=drone.y+drone.vy*.12>ty;return}}holding=window.__sab==='up';return}window.__apOk()}")
        await self.js("window.__noOver=true;const __so=showOver;showOver=function(m,r){if(window.__noOver){window.__overArgs=[m,r];return}__so(m,r)};const __sre=showRaceEnd,__srr=showRaceRevive;showRaceEnd=function(m){if(window.__noOver){window.__raceArgs=['end',m];return}__sre(m)};showRaceRevive=function(m){if(window.__noOver){window.__raceArgs=['rev',m];return}__srr(m)}")
        await self.pg.add_style_tag(content="""#endc .cta{font-family:var(--display),system-ui;font-size:30px;color:#ffe680;line-height:1.15;margin-bottom:4px;text-shadow:0 0 18px rgba(255,200,60,.6)}
          #ovl .t{white-space:normal}""")

    async def seg(self, setup, warm=60):
        await self.js("freezeT=0;holeOn=false;holeLeft=0;holeFx=0;zapT=0;ghostT=0;portals=[];window.__sab=false;try{holeWindStop()}catch(e){}")
        await self.js(setup)
        await self.js(f"for(let i=0;i<{warm};i++){{__tick(1/60);battery=100}}")

    async def endc(self, cta=''):
        html = (f"<div class=cta>{cta}</div>" if cta else '') + "<h1>DRONE<br><span>RUSH</span></h1><p>Juega gratis en Telegram</p><div class=tg><i>✈</i>@dronerushhbot</div><small>Sin descargar nada · PvP · Torneos · Skins</small>"
        await self.pg.evaluate("h=>{const e=document.getElementById('endc');e.innerHTML=h;e.style.display='flex'}", html)

    async def pos(self, top):
        await self.pg.evaluate("t=>document.getElementById('ovl').style.setProperty('top',t,'important')", top)

    async def card_show(self, on=True):
        await self.pg.evaluate('''on=>{let d=document.getElementById('cshow');if(!on){if(d)d.remove();return}
          d=document.createElement('div');d.id='cshow';d.style.cssText='position:fixed;inset:0;z-index:49;display:flex;align-items:center;justify-content:center;padding-top:130px;background:rgba(8,4,20,.72)';
          const im=document.createElement('img');im.src=document.getElementById('rcImg').src;im.style.cssText='width:300px;height:300px;border-radius:22px;box-shadow:0 10px 50px rgba(255,120,220,.5);transform:rotate(-3deg)';
          d.append(im);document.body.append(d)}''', on)

    async def m(self):
        return await self.js('Math.floor(dist/PXM)')

    async def until_dead(self, maxs=12, speed=1.0, every=None):
        """juega hasta que el dron se estrella (god off)"""
        i = 0
        while i < maxs * FPS:
            st = await self.js('state')
            if st != 'play': break
            sp = self.speed * speed; sub = max(1, int(round(2 * sp))); dt = (1 / FPS) * sp / sub
            await self.js(f'for(let i=0;i<{sub};i++){{if(state!=="play")break;__tick({dt});battery=Math.max(battery,60)}}')
            if every: await every(i)
            await self.shot(); i += 1

    async def after(self, seconds):
        """sigue renderizando tras el choque (explosión)"""
        for i in range(int(seconds * FPS)):
            await self.js('__tick(1/30)'); await self.shot()

def encode(dir_, out):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', f'{dir_}/f%05d.jpg',
                    '-vf', 'scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
                    '-movflags', '+faststart', out], check=True)

def newdir(r, name):
    r.dir = f'/tmp/claude-0/s/vid/frames_{name}'
    shutil.rmtree(r.dir, ignore_errors=True); os.makedirs(r.dir); r.n = 0
