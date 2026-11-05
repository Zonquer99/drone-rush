import sys;sys.path.insert(0,'/tmp/claude-0/s/trailer/scripts')
from assemble import *
WH=(255,255,255)
# 1 · amanecer
ai('s1','s1.png',3.6,dict(z0=1.0,z1=1.16,px=.15,py=-.1,par=.28,warm=.35),[dust(),flare((.6,.30),.4)],
   texts=[dict(lines=['TODO EMPEZÓ'],t0=.5,t1=3.5,y=.70,size=120),dict(lines=['CON UN DRON…'],t0=1.2,t1=3.5,y=.70+.065,size=120)],fin=.8)
# 2 · despegue
ai('s2','s2.png',2.5,dict(z0=1.05,z1=1.30,par=.35,warm=.3),[dust(160,(1,.8,.5),(2,6),(80,260),-60),shake(5,22),flare((.8,.1),.3)],
   texts=[dict(lines=['…Y UN CIELO'],t0=.2,t1=2.5,y=.72,size=120),dict(lines=['LLENO DE PELIGROS'],t0=.6,t1=2.5,y=.72+.065,size=120,glow=(255,90,60))])
flash_frames(4)
# 3 · juego: viñedos rozando torres
game('g1','G1.mp4',dur=5.2,texts=[dict(lines=['ESQUIVA'],t0=.2,t1=1.6,y=.42,size=150,glow=(90,200,255))])
# 4 · tormenta (IA)
ai('s3','s3.png',2.6,dict(z0=1.0,z1=1.14,px=-.15,par=.25),[rain(),flashes([.15,1.3,1.45,2.1]),shake(3,9)],
   texts=[dict(lines=['SOBREVIVE'],t0=.3,t1=2.6,y=.70,size=130,glow=(120,190,255)),dict(lines=['A LA TORMENTA'],t0=.6,t1=2.6,y=.765,size=130,glow=(120,190,255))])
flash_frames(3,.8)
game('g2','G2.mp4',dur=3.4,start=.3)
# 5 · jefe (IA)
ex,ey=find_red(IMG+'s4.png')
ai('s4','s4.png',3.0,dict(z0=1.0,z1=1.2,py=.15,par=.3),[glow_at((ex,ey),r=160,pulse=1.6,amt=.9),dust(120,(1,.3,.15),(1.5,4),(-40,40),-90),shake(4,6,1.6,3)],
   texts=[dict(lines=['DERROTA A'],t0=.4,t1=3.0,y=.70,size=130,glow=(255,60,60)),dict(lines=['LOS JEFES'],t0=.7,t1=3.0,y=.765,size=150,glow=(255,60,60))])
flash_frames(3,.9)
game('g3','G3.mp4',dur=4.8,start=.4)
# 6 · montaje rápido
game('g4a','G4a.mp4',texts=[dict(lines=['GRAVEDAD','AL REVÉS'],t0=0,t1=1.2,y=.55,size=110,glow=(255,120,245))],flash_in=.12)
game('g4b','G4b.mp4',dur=1.9,texts=[dict(lines=['MODO GIGANTE'],t0=0,t1=1.9,y=.55,size=110,glow=(255,140,60))],flash_in=.12)
game('g4c','G4c.mp4',texts=[dict(lines=['LLUVIA','DE MONEDAS'],t0=0,t1=1.3,y=.55,size=110,glow=(255,210,80))],flash_in=.12)
flash_frames(4)
# 7 · espacio (IA)
ai('s5','s5.png',3.6,dict(z0=1.12,z1=1.0,py=-.2,par=.2),[stars_twinkle(),flare((.45,.62),.35,(.7,.85,1))],
   texts=[dict(lines=['¿HASTA DÓNDE'],t0=.5,t1=3.6,y=.30,size=140,glow=(160,140,255)),dict(lines=['LLEGARÁS?'],t0=.9,t1=3.6,y=.375,size=160,glow=(160,140,255))])
game('g5','G5.mp4',dur=3.6,start=.2,flash_in=.15)
# 8 · cartel final
import assemble as A
MARK['end']=A.n/FPS
bg=cv2.imread(IMG+'s5.png');bg=cv2.resize(bg,(W,H));bg=cv2.GaussianBlur(bg,(0,0),18).astype(np.float32)/255.*.45
for i in range(int(3.8*FPS)):
    t=i/FPS;f=bg.copy()
    f=over(f,text_layer(['DRONE'],t+1,0,99,y=.30,fnt=RUSSO,size=190,glow=(255,180,90),track=4))
    f=over(f,text_layer(['RUSH'],t+1,0,99,y=.30+.105,fnt=RUSSO,size=190,col=(255,179,107),glow=(255,120,40),track=4))
    if t>.4:
        L=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(L);a=int(255*min(1,(t-.4)/.4))
        f1=font(BALOO,58);s1='Juega gratis en Telegram';d.text(((W-d.textlength(s1,font=f1))/2,H*.56),s1,font=f1,fill=(240,232,255,a))
        f2=font(BALOO,66);s2='@dronerushhbot';tw=d.textlength(s2,font=f2);bx=(W-tw)/2-44;by=int(H*.63)
        d.rounded_rectangle((bx,by,bx+tw+88,by+110),radius=40,fill=(42,163,224,a));d.text((bx+44,by+12),s2,font=f2,fill=(255,255,255,a))
        f3=font(BALOO,40);s3='Mundos · Jefes · PvP · Torneos';d.text(((W-d.textlength(s3,font=f3))/2,H*.74),s3,font=f3,fill=(200,190,230,a))
        arr=np.array(L).astype(np.float32)/255.;f=over(f,arr)
    put(f)
print('frames',A.n,'dur',A.n/FPS);print('MARK',MARK)
import json;json.dump(MARK,open(T+'marks.json','w'))
