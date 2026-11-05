import os,sys;os.environ['OUTDIR']='/tmp/claude-0/s/trailer/fr_v5';sys.path.insert(0,'/tmp/claude-0/s/trailer/scripts')
import assemble as A
from assemble import *
ex,ey=find_red(IMG+'eye.png');bx,by=find_red(IMG+'s4.png')
RED=(255,40,40)
# 1 · el ojo se abre
ai('eye1','eye.png',1.7,dict(z0=1.0,z1=1.45,par=.25),[iris((ex,ey),.15,.7),glow_at((ex,ey),r=170,pulse=1.6,amt=.9),shake(12,22,.6,1.1),glitch([.7,1.4]),dust(70,(1,.3,.2),(1.5,3.5),(-20,20),-40)],
   texts=[dict(lines=['NO MIRES'],t0=.05,t1=1.7,y=.70,size=160,glow=RED),dict(lines=['AL OJO ROJO'],t0=.35,t1=1.7,y=.70+.085,size=160,col=(255,70,70),glow=RED)])
# 2 · el jefe entero
ai('boss','s4.png',1.0,dict(z0=1.35,z1=1.0,par=.3),[glow_at((bx,by),r=150,pulse=2.5,amt=.9),shake(10,16,0,.5),dust(110,(1,.3,.15),(1.5,4),(-40,40),-90)],
   texts=[dict(lines=['APARECE A LOS'],t0=0,t1=1.0,y=.70,size=110,glow=RED),dict(lines=['1.500 METROS'],t0=.1,t1=1.0,y=.70+.06,size=150,col=(255,90,90),glow=RED)])
flash_frames(2,.9)
# 3 · el juego
game('g','V5_boss3.mp4',start=.1,dur=8.6,texts=[dict(lines=['SOBREVIVE','15 SEGUNDOS'],t0=.9,t1=2.4,y=.62,size=120,glow=RED),dict(lines=['¿AGUANTAS?'],t0=4.3,t1=5.6,y=.62,size=140,glow=RED)])
# 4 · vuelve más fuerte
ai('eye2','eye.png',1.4,dict(z0=1.45,z1=1.6,par=.2),[glow_at((ex,ey),r=200,pulse=3,amt=1.1),glitch([0,.35,.7,1.0],.1,40),iris((ex,ey),-1,0,closing=(1.05,1.38)),tint((1,.3,.3),.25)],
   texts=[dict(lines=['Y CADA VEZ'],t0=0,t1=1.15,y=.68,size=130,glow=RED),dict(lines=['VUELVE MÁS FUERTE'],t0=.2,t1=1.15,y=.68+.07,size=130,col=(255,80,80),glow=RED)])
# 5 · cartel final
A.MARK['end']=A.n/FPS
bg=cv2.imread(IMG+'s4.png');bg=cv2.resize(bg,(W,H));bg=cv2.GaussianBlur(bg,(0,0),16).astype(np.float32)/255.*.4
for i in range(int(2.6*FPS)):
    t=i/FPS;f=bg.copy()
    f=over(f,text_layer(['¿LLEGAS A LOS'],t+1,0,99,y=.30,size=130,glow=RED))
    f=over(f,text_layer(['1.500 M?'],t+1,0,99,y=.37,size=200,col=(255,80,80),glow=RED))
    if t>.3:
        L=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(L);a=int(255*min(1,(t-.3)/.4))
        f0=font(RUSSO,96);s0='DRONE RUSH';d.text(((W-d.textlength(s0,font=f0))/2,H*.55),s0,font=f0,fill=(255,179,107,a))
        f1=font(BALOO,54);s1='Juega gratis en Telegram';d.text(((W-d.textlength(s1,font=f1))/2,H*.62),s1,font=f1,fill=(240,232,255,a))
        f2=font(BALOO,64);s2='@dronerushhbot';tw=d.textlength(s2,font=f2);bx2=(W-tw)/2-44;by2=int(H*.68)
        d.rounded_rectangle((bx2,by2,bx2+tw+88,by2+108),radius=40,fill=(42,163,224,a));d.text((bx2+44,by2+12),s2,font=f2,fill=(255,255,255,a))
        f=over(f,np.array(L).astype(np.float32)/255.)
    put(f)
print('frames',A.n,A.n/FPS,A.MARK)
import json;json.dump(A.MARK,open('/tmp/claude-0/s/trailer/marks_v5.json','w'))
