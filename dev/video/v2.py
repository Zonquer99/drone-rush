import os,sys;os.environ['OUTDIR']='/tmp/claude-0/s/trailer/fr_v2';sys.path.insert(0,'/tmp/claude-0/s/trailer/scripts')
import assemble as A
from assemble import *
gx,gy=find_col(IMG+'mother.png',1)
GR=(90,255,150)
ai('m1','mother.png',3.2,dict(z0=1.0,z1=1.15,py=-.15,par=.3,warm=.1),[glow_at((gx,gy),col=(.3,1,.5),r=220,pulse=.8,amt=.5),dust(80,(1,.85,.6),(1.5,3.5),(10,30),-6),shake(3,7,1.6,3.2)],
   texts=[dict(lines=['NO ESTAMOS'],t0=.3,t1=3.2,y=.70,size=160,glow=GR),dict(lines=['SOLOS'],t0=.8,t1=3.2,y=.70+.085,size=200,col=(140,255,180),glow=GR)],fin=.5)
ai('m2','mother.png',2.2,dict(z0=1.45,z1=1.7,py=-.4,par=.35),[glow_at((gx,gy),col=(.3,1,.5),r=260,pulse=2.2,amt=.9),flashes([.6,1.4],.15,(.6,1,.7),.6),shake(7,16,.5,2.2)],
   texts=[dict(lines=['HA LLEGADO'],t0=.1,t1=2.2,y=.68,size=130,glow=GR),dict(lines=['LA NAVE NODRIZA'],t0=.4,t1=2.2,y=.68+.07,size=140,col=(140,255,180),glow=GR)])
flash_frames(3,.9)
game('g','V2_boss.mp4',texts=[dict(lines=['ESQUIVA'],t0=1.8,t1=3.2,y=.62,size=150,glow=GR),dict(lines=['TODO'],t0=2.1,t1=3.2,y=.62+.07,size=150,col=(140,255,180),glow=GR)])
flash_frames(3,.8)
ai('sp','s5.png',2.4,dict(z0=1.1,z1=1.0,py=-.2,par=.2),[stars_twinkle(),flare((.45,.62),.35,(.7,.85,1))],
   texts=[dict(lines=['TE ESPERA A'],t0=.2,t1=2.4,y=.30,size=130,glow=GR),dict(lines=['5.500 METROS'],t0=.5,t1=2.4,y=.37,size=170,col=(140,255,180),glow=GR)])
A.MARK['end']=A.n/FPS
bg=cv2.imread(IMG+'mother.png');bg=cv2.resize(bg,(W,H));bg=cv2.GaussianBlur(bg,(0,0),16).astype(np.float32)/255.*.4
for i in range(int(3.2*FPS)):
    t=i/FPS;f=bg.copy()
    f=over(f,text_layer(['¿PODRÁS'],t+1,0,99,y=.30,size=150,glow=GR))
    f=over(f,text_layer(['DERROTARLA?'],t+1,0,99,y=.385,size=170,col=(140,255,180),glow=GR))
    if t>.3:
        L=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(L);a=int(255*min(1,(t-.3)/.4))
        f0=font(RUSSO,96);s0='DRONE RUSH';d.text(((W-d.textlength(s0,font=f0))/2,H*.55),s0,font=f0,fill=(255,179,107,a))
        f1=font(BALOO,54);s1='Juega gratis en Telegram';d.text(((W-d.textlength(s1,font=f1))/2,H*.62),s1,font=f1,fill=(240,232,255,a))
        f2=font(BALOO,64);s2='@dronerushhbot';tw=d.textlength(s2,font=f2);bx2=(W-tw)/2-44;by2=int(H*.68)
        d.rounded_rectangle((bx2,by2,bx2+tw+88,by2+108),radius=40,fill=(42,163,224,a));d.text((bx2+44,by2+12),s2,font=f2,fill=(255,255,255,a))
        f=over(f,np.array(L).astype(np.float32)/255.)
    put(f)
print('frames',A.n,A.n/FPS,A.MARK)
import json;json.dump(A.MARK,open('/tmp/claude-0/s/trailer/marks_v2.json','w'))
