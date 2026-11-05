import asyncio,sys,shutil,subprocess
sys.path.insert(0,'/tmp/claude-0/s/vid')
import reclib
mode=sys.argv[1]
if mode=='land': reclib.W,reclib.H,reclib.DSF=960,540,2.0
else: reclib.W,reclib.H,reclib.DSF=540,810,2.0
from playwright.async_api import async_playwright
from reclib3 import *
import reclib3,reclib2
AP=open('/tmp/claude-0/s/vid/ap3.js').read()
OUT='/tmp/claude-0/s/cg/'
async def main():
  async with async_playwright() as p:
    r=Rec3('cg'+mode)
    # usar la versión de portales
    orig=r.pg if hasattr(r,'pg') else None
    reclib.Rec.start.__defaults__
    await r.start(p)
    await r.pg.goto('file:///tmp/claude-0/s/vid/rec_cg.html');await r.pg.wait_for_timeout(500)
    await r.pg.evaluate("l=>localStorage.setItem('dronerush.v1',JSON.stringify({gen:2,named:true,pilot:'Zonquer',lang:'en',sound:false,music:false,games:30,uG:30,uB:4000,best:4000,unl:['shop','free','mis','pass','inv','adv','pvp'],unlNew:[]}))",'en')
    await r.pg.reload();await r.pg.wait_for_timeout(700)
    await r.pg.add_style_tag(content=reclib.OVL_CSS+reclib2.EPIC_CSS)
    await r.pg.evaluate("()=>{const o=document.createElement('div');o.id='ovl';document.body.append(o);const e=document.createElement('div');e.id='endc';document.body.append(e);for(const id of ['fl','vig']){const d=document.createElement('div');d.id=id;document.body.append(d)}}")
    await r.js(reclib.AP_JS);await r.js("window.__manual=true");await r.js(reclib2.AP2);await r.js(AP)
    await r.js("M.owned=['clasico','emperador','rayo','ovni','glaciar','enjambre'];M.best=9000")
    segs=[("M.skin='enjambre';startGame(1);dist=3168*PXM;bossNext=99999;window.__dare=true;window.__dareC=14",20,5.5,'hive'),
          ("M.skin='rayo';startGame(1);dist=4100*PXM;bossNext=99999;zapNext=4118",30,3.3,None),
          ("M.skin='glaciar';startGame(1);dist=3480*PXM;bossNext=3481;nextFreeze=99999;window.__dare=true;window.__dareC=16",100,5.0,'boss'),
          ("M.skin='ovni';startGame(1);dist=4960*PXM;bossNext=99999;window.__dare=true",100,3.2,None)]
    newdir(r,'cg'+mode)
    for setup,warm,secs,kind in segs:
      await r.js(AP);await r.js("freezeT=0;window.__dare=false;window.__god=true;evNext=99999;hintT=0")
      await r.js(setup);await r.js("worldNow=wIdx(dist/PXM);hintT=0;evK='';evT=0;evNext=99999;dailyRun=null");await r.js(f"for(let i=0;i<{warm};i++){{__tick(1/60);battery=100}}");await r.js("bigM=null")
      if kind=='boss': await r.js("for(let i=0;i<110&&boss&&boss.ph==='in';i++){__tick(1/60);battery=100};if(boss){boss.ph='fight';boss.t=0;boss.lv=6;boss.shotT=.15;boss.lasT=.8;boss.mineT=.4}")
      if kind=='bee': await r.js("swarmCh=2;swarmNext=99999;window.__god=false;invuln=0;obs=obs.filter(o=>o.x<drone.x||o.x>drone.x+420);obs.push({type:'enemy',x:drone.x+190,y0:drone.y,amp:0,ph:0});window.__ap=function(){holding=drone.y+drone.vy*.16>(window.__ty||drone.y)}")
      async def ev(i):
        if kind=='bee' and i==1: await r.js("window.__ty=obs.filter(o=>o.type==='enemy').map(o=>enemyY(o))[0]||drone.y")
        if kind=='bee' and i==45: await r.js(AP);await r.js("window.__god=true")
      await r.play(secs,every=ev)
    size='1920:1080' if mode=='land' else '1080:1620'
    subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',r.dir+'/f%05d.jpg','-vf',f'scale={size}:flags=lanczos,format=yuv420p','-c:v','libx264','-crf','19','-an',OUT+f'gp2_{mode}.mp4'],check=True)
    print('errs',r.errs);await r.b.close()
asyncio.run(main())
