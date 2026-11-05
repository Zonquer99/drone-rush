import asyncio,base64
from playwright.async_api import async_playwright
OUT='/home/claude/drone-rush/app/assets/'
JS=r"""
(([kind,S])=>{const c=document.createElement('canvas');c.width=c.height=S;const g=c.getContext('2d');
 const bg=()=>{const gr=g.createRadialGradient(S*.5,S*.62,S*.05,S*.5,S*.5,S*.75);gr.addColorStop(0,'#ffb36b');gr.addColorStop(.32,'#c45f72');gr.addColorStop(.62,'#4a2f73');gr.addColorStop(1,'#1b1638');g.fillStyle=gr;g.fillRect(0,0,S,S);
   g.fillStyle='rgba(255,214,150,.9)';g.beginPath();g.arc(S*.5,S*.66,S*.16,0,6.28);g.fill();
   g.fillStyle='#283146';g.beginPath();g.moveTo(0,S);for(let x=0;x<=S;x+=S/40)g.lineTo(x,S*.8-Math.sin(x/S*7)*S*.03);g.lineTo(S,S);g.fill()};
 const drone=(sc,y)=>{g.save();g.translate(S/2,y);g.rotate(-.08);g.scale(sc,sc);GS=sc;t=1.3;
   g.save();g.globalCompositeOperation='lighter';const a=g.createRadialGradient(0,0,4,0,0,60);a.addColorStop(0,'rgba(255,220,180,.55)');a.addColorStop(1,'rgba(255,200,150,0)');g.fillStyle=a;g.beginPath();g.arc(0,0,60,0,6.28);g.fill();g.restore();
   droneShape(g,skinById('clasico'),false);g.restore()};
 if(kind==='full'){bg();drone(S/95,S*.47)}
 else if(kind==='bg'){bg()}
 else if(kind==='fg'){drone(S/150,S*.5)}
 else if(kind==='splash'){g.fillStyle='#1b1638';g.fillRect(0,0,S,S);drone(S/260,S*.42);
   g.textAlign='center';g.font=`${S*.09}px "Russo One"`;g.fillStyle='#fff6ea';g.fillText('DRONE',S/2,S*.6);g.fillStyle='#ffb36b';g.fillText('RUSH',S/2,S*.69)}
 return c.toDataURL('image/png')})
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch();pg=await b.new_page()
    for u in ['**/supabase.min.js','**/telegram.org/**','**/libtl.com/**']:
      await pg.route(u,lambda r:r.fulfill(body='',content_type='text/javascript'))
    await pg.goto('file:///tmp/claude-0/s/vid/rec.html');await pg.wait_for_timeout(600)
    for kind,S,name in [('full',1024,'icon-only.png'),('bg',1024,'icon-background.png'),('fg',1024,'icon-foreground.png'),('splash',2732,'splash.png'),('splash',2732,'splash-dark.png')]:
      d=await pg.evaluate("a=>__t('('+a[0]+')('+JSON.stringify(a[1])+')')",[JS,[kind,S]])
      open(OUT+name,'wb').write(base64.b64decode(d.split(',')[1]))
    await b.close()
asyncio.run(main())
