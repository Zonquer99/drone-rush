import asyncio,sys
sys.path.insert(0,'/tmp/claude-0/s/vid')
from playwright.async_api import async_playwright
from reclib3 import *
async def main():
  async with async_playwright() as p:
    r=Rec3('dbg');await r.start(p)
    await r.js("M.skin='clasico';startGame(1);dist=1300*PXM;hintT=0;window.__god=false;evNext=99999;bossNext=99999;for(let i=0;i<120;i++){__tick(1/60);battery=100};obs=[];for(let k=0;k<4;k++)obs.push({type:'pylon',x:drone.x+110+k*170,w:44,top:k%2?110:150,bot:k%2?190:230});pwGet('giant');acc=-1e9;window.__ap=function(){holding=drone.y+drone.vy*.16>320}")
    for k in range(6):
      print(await r.js("for(let i=0;i<12;i++)__tick(1/30);[Math.round(drone.y),obs.map(o=>o.type+':'+Math.round(o.x)+(o.dead?'D':'')).join(' '),state,pwK,Math.round(speed)]"))
    await r.b.close()
asyncio.run(main())
