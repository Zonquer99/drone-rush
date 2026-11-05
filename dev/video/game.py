import asyncio,sys
sys.path.insert(0,'/tmp/claude-0/s/vid')
from playwright.async_api import async_playwright
from reclib3 import *
AP=open('/tmp/claude-0/s/vid/ap3.js').read()
import os
ONLY=os.environ.get('ONLY','').split(',') if os.environ.get('ONLY') else None
async def seg(r,name,setup,secs,every=None,speed=1.0,warm=40):
  if ONLY and name not in ONLY: return
  newdir(r,name);await r.js(AP)
  await r.js("freezeT=0;holeOn=false;portals=[];window.__sab=false;window.__dare=false;try{holeWindStop()}catch(e){}")
  await r.js(setup);await r.js("worldNow=wIdx(dist/PXM)");await r.js(f"for(let i=0;i<{warm};i++){{__tick(1/60);battery=100}}");await r.js("if(!window.__keepBanner)bigM=null;window.__keepBanner=false")
  await r.play(secs,speed=speed,every=every)
  encode(r.dir,f'/tmp/claude-0/s/trailer/{name}.mp4')
async def main():
  async with async_playwright() as p:
    r=Rec3('G0');await r.start(p);await r.js(AP)
    await r.js("M.owned=['clasico','emperador','rayo','ovni'];M.best=9000;M.skin='clasico'")
    await r.text('')
    # G1 viñedos: rozando torres, cámara lenta en cada «¡por los pelos!»
    st={'n':0,'slow':0}
    async def e1(i):
      n=await r.js('nearRun')
      await r.js("if(obs.filter(o=>o.x>drone.x).length<2&&!obs.some(o=>o.x>LW-40))spawn()")
      if n>st['n']:st['n']=n;st['slow']=16;r.speed=.35;r.punch(.05,.25)
      if st['slow']>0:
        st['slow']-=1
        if st['slow']==0:r.speed=1
    await seg(r,'G1',"M.skin='clasico';M.scene='base';startGame(1);dist=760*PXM;hintT=0;window.__god=true;shields=0;window.__dare=true;evNext=99999;bossNext=99999",6.0,every=e1,warm=260)
    # G2 tormenta + apagón
    async def e2(i):
      if i==45: await r.js("evStart('dark')")
    await r.js('window.__keepBanner=true');await seg(r,'G2',"M.skin='rayo';startGame(1);dist=3990*PXM;hintT=0;window.__god=true;shields=0;evNext=99999;bossNext=99999;zapNext=999999",4.0,every=e2,warm=90)
    # G3 jefe
    async def e3(i):
      if i==105: await r.js("if(boss&&boss.ph==='fight')boss.t=BOSS_DUR-.05")
    await seg(r,'G3',"M.skin='emperador';startGame(1);dist=4495*PXM;hintT=0;window.__god=true;shields=0;evNext=99999;bossNext=4500;royal=0",5.5,every=e3,warm=20)
    # G4 montaje: gravedad, gigante, lluvia de monedas
    await seg(r,'G4a',"M.skin='ovni';startGame(1);dist=3350*PXM;hintT=0;window.__god=true;evNext=99999;bossNext=99999;evStart('grav');for(let i=0;i<70;i++)__tick(1/60)",1.2,warm=10)
    await seg(r,'G4b',"M.skin='clasico';startGame(1);dist=1300*PXM;hintT=0;window.__god=true;evNext=99999;bossNext=99999;for(let i=0;i<120;i++){__tick(1/60);battery=100};window.__god=false;obs=[];for(let k=0;k<4;k++)obs.push({type:'pylon',x:drone.x+110+k*170,w:44,top:k%2?110:150,bot:k%2?190:230});pwGet('giant');acc=-1e9;window.__cruise=320;window.__sab=false;window.__ap=function(){holding=drone.y+drone.vy*.16>320}",2.2,warm=1,speed=.55)
    await seg(r,'G4c',"M.skin='rayo';startGame(1);dist=3195*PXM;hintT=0;window.__god=true;evNext=99999;bossNext=99999;zapNext=999999",1.3,warm=50)
    # G5 espacio
    await r.js('window.__keepBanner=true');await seg(r,'G5',"M.skin='emperador';startGame(1);dist=4930*PXM;hintT=0;window.__god=true;evNext=99999;bossNext=99999;window.__dare=true",4.5,warm=150)
    print('errs',r.errs)
    await r.b.close()
asyncio.run(main())
