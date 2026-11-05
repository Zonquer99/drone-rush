import asyncio,sys,os
sys.path.insert(0,'/tmp/claude-0/s/vid')
from playwright.async_api import async_playwright
from reclib3 import *
AP=open('/tmp/claude-0/s/vid/ap3.js').read()
OUT='/tmp/claude-0/s/trailer/'
async def seg(r,name,setup,secs,every=None,warm=10):
  newdir(r,name);await r.js(AP)
  await r.js("freezeT=0;holeOn=false;portals=[];window.__sab=false;window.__dare=false")
  await r.js(setup);await r.js("worldNow=wIdx(dist/PXM)");await r.js(f"for(let i=0;i<{warm};i++){{__tick(1/60);battery=100}}")
  await r.play(secs,every=every)
  encode(r.dir,OUT+name+'.mp4')
window_near=70;slow_len=14;base_speed=1.0
def slowmo_near(r,defeat_at=None):
  st={'slow':0}
  async def ev(i):
    d=await r.js("Math.min(999,...obs.filter(o=>o.type==='shot'||o.type==='mine').map(o=>Math.hypot(o.x-drone.x,o.y-drone.y)))")
    las=await r.js("obs.some(o=>o.type==='laser'&&o.warn<=0&&o.on>0)")
    if i==8: await r.js("if(boss){boss.lv=window.__blv||boss.lv}")
    if (d<window_near or las) and st['slow']<=0: st['slow']=slow_len;r.speed=.3;r.punch(.05,.2 if las else .05)
    if st['slow']>0:
      st['slow']-=1
      if st['slow']==0:r.speed=base_speed
    if defeat_at and i==defeat_at: await r.js("if(boss&&boss.ph==='fight')boss.t=BOSS_DUR-.05")
  return ev
async def main():
  async with async_playwright() as p:
    r=Rec3('GX');await r.start(p);await r.text('')
    await r.js("M.owned=['clasico','emperador','rayo','ovni','glaciar'];M.best=9000")
    global window_near,slow_len,base_speed
    window_near,slow_len,base_speed=42,7,1.4;r.speed=1.4
    await r.js("window.__blv=6")
    await seg(r,'V5_boss3',"M.skin='glaciar';M.scene='base';startGame(1);dist=1488*PXM;hintT=0;window.__god=true;shields=0;evNext=99999;nextFreeze=99999;window.__dare=true;window.__dareC=16",9.5,every=slowmo_near(r,235),warm=20)
    return
    await seg(r,'V2_boss',"M.skin='emperador';startGame(1);dist=5496*PXM;hintT=0;window.__god=true;shields=0;evNext=99999;royal=0;bossNext=5500",10.0,every=slowmo_near(r,250),warm=20)
    print('errs',r.errs)
    await r.b.close()
asyncio.run(main())
