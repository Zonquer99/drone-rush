# Anima una imagen fija como plano de cine: profundidad (paralaje), cámara, partículas y luz.
import cv2,numpy as np,math,os,sys
sys.path.insert(0,os.path.dirname(__file__))
from depth import depth
W,H,FPS=1080,1920,30
ease=lambda u:u*u*(3-2*u)
def prep(path,margin=1.14):
    im=cv2.imread(path);h,w=im.shape[:2];s=max(W*margin/w,H*margin/h)
    im=cv2.resize(im,(int(w*s),int(h*s)),interpolation=cv2.INTER_LANCZOS4)
    d=depth(im).astype(np.float32);return im,d
def grade(f,warm=0.0,contrast=1.08,sat=1.1):
    f=f.astype(np.float32)/255.
    if warm: f[...,2]*=1+warm*.10;f[...,0]*=1-warm*.08
    f=(f-.5)*contrast+.5
    g=f.mean(2,keepdims=True);f=g+(f-g)*sat
    return f
class Scene:
    def __init__(s,path,dur,z0=1.0,z1=1.12,px=0.0,py=0.0,par=0.10,warm=0.0,seed=1):
        s.im,s.d=prep(path);s.dur=dur;s.z0,s.z1,s.px,s.py,s.par,s.warm=z0,z1,px,py,par,warm
        s.h,s.w=s.im.shape[:2];s.rng=np.random.default_rng(seed)
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32);s.xx=xx-W/2;s.yy=yy-H/2
        s.fx=[];s.parts=[]
    def frame(s,i):
        n=int(s.dur*FPS);u=i/max(1,n-1);e=ease(u)
        z=s.z0+(s.z1-s.z0)*e
        cx,cy=s.w/2+s.px*e*s.w*.08,s.h/2+s.py*e*s.h*.08
        # 1ª pasada sin profundidad para leer la profundidad
        mx=cx+s.xx/z;my=cy+s.yy/z
        dd=cv2.remap(s.d,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        zz=z*(1+s.par*e*(dd-.4))
        mx=cx+s.xx/zz+s.px*e*s.w*.03*(dd-.5);my=cy+s.yy/zz+s.py*e*s.h*.02*(dd-.5)
        f=cv2.remap(s.im,mx,my,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        f=grade(f,s.warm)
        t=i/FPS
        for fx in s.fx:f=fx(s,f,t,u,dd)
        return f
    def render(s,outdir,start=0):
        n=int(s.dur*FPS)
        for i in range(n):
            f=s.frame(i);f=finish(f,i+start)
            cv2.imwrite(f'{outdir}/f{start+i:05d}.jpg',f,[cv2.IMWRITE_JPEG_QUALITY,92])
        return start+n
_grain=None
def finish(f,k):
    global _grain
    if _grain is None:_grain=[np.random.default_rng(j).normal(0,1,(H//2,W//2)).astype(np.float32) for j in range(8)]
    g=cv2.resize(_grain[k%8],(W,H))[...,None]*.018
    yy,xx=np.mgrid[0:H,0:W];v=1-.38*(((xx-W/2)/(W*.75))**2+((yy-H/2)/(H*.7))**2)
    f=f*v[...,None].astype(np.float32)+g
    return (np.clip(f,0,1)*255).astype(np.uint8)
# ---------- efectos ----------
def dust(n=90,col=(1,.85,.6),size=(1.5,4),speed=(10,40),rise=-8):
    st={}
    def fx(s,f,t,u,dd):
        if 'p' not in st:r=s.rng;st['p']=np.c_[r.uniform(0,W,n),r.uniform(0,H,n),r.uniform(*size,n),r.uniform(*speed,n),r.uniform(0,6.28,n)]
        o=np.zeros((H,W),np.float32)
        for x,y,sz,sp,ph in st['p']:
            X=int((x+sp*t+8*math.sin(t*.7+ph))%W);Y=int((y+rise*t+6*math.cos(t*.5+ph))%H)
            cv2.circle(o,(X,Y),int(sz),.55+.45*math.sin(t*2+ph),-1,cv2.LINE_AA)
        o=cv2.GaussianBlur(o,(0,0),1.6)[...,None]
        return f+o*np.array(col[::-1],np.float32)*.5
    return fx
def rain(n=260,ang=.25,spd=2600,alpha=.35):
    st={}
    def fx(s,f,t,u,dd):
        if 'p' not in st:r=s.rng;st['p']=np.c_[r.uniform(0,W,n),r.uniform(0,H,n),r.uniform(.6,1.2,n)]
        o=np.zeros((H,W),np.float32)
        for x,y,k in st['p']:
            Y=(y+spd*k*t)%H;X=(x-spd*k*t*ang)%W;L=60*k
            cv2.line(o,(int(X),int(Y)),(int(X-L*ang),int(Y+L)),.8,1,cv2.LINE_AA)
        return f+cv2.GaussianBlur(o,(0,0),.8)[...,None]*np.array([1,.95,.85],np.float32)*alpha
    return fx
def flashes(times,dur=.18,col=(.85,.9,1),amt=.9):
    def fx(s,f,t,u,dd):
        a=0
        for t0 in times:
            if t0<=t<t0+dur:k=(t-t0)/dur;a=max(a,(1-k)*(1 if int((t-t0)*40)%3 else .4))
        return f+a*amt*np.array(col[::-1],np.float32) if a>0 else f
    return fx
def shake(amp=6,freq=18,t0=0,t1=99):
    def fx(s,f,t,u,dd):
        if not(t0<=t<t1):return f
        dx=amp*math.sin(t*freq*6.3);dy=amp*math.cos(t*freq*5.1+1)
        M=np.float32([[1,0,dx],[0,1,dy]]);return cv2.warpAffine(f,M,(W,H),borderMode=cv2.BORDER_REFLECT)
    return fx
def glow_at(xy_rel,col=(1,.15,.1),r=140,pulse=2.2,amt=.8):
    def fx(s,f,t,u,dd):
        x,y=int(xy_rel[0]*W),int(xy_rel[1]*H);a=amt*(.55+.45*math.sin(t*pulse*6.28))
        yy,xx=np.ogrid[0:H,0:W];g=np.exp(-((xx-x)**2+(yy-y)**2)/(2*r*r)).astype(np.float32)[...,None]
        return f+g*a*np.array(col[::-1],np.float32)
    return fx
def flare(xy_rel,amt=.35,col=(1,.85,.55)):
    def fx(s,f,t,u,dd):
        x,y=xy_rel[0]*W,xy_rel[1]*H;yy,xx=np.ogrid[0:H,0:W]
        g=np.exp(-((xx-x)**2+(yy-y)**2)/(2*260**2)).astype(np.float32)
        sw=np.exp(-((yy-y)**2)/(2*6**2)).astype(np.float32)*np.exp(-((xx-x)**2)/(2*500**2))
        a=amt*(.85+.15*math.sin(t*1.3))
        return f+(g*.8+sw*.6)[...,None]*a*np.array(col[::-1],np.float32)
    return fx
def fade(fin=.0,fout=.0,col=0):
    def fx(s,f,t,u,dd):
        a=1.0
        if fin and t<fin:a=t/fin
        if fout and t>s.dur-fout:a=min(a,(s.dur-t)/fout)
        return f*a+col*(1-a)
    return fx
def stars_twinkle(n=140):
    st={}
    def fx(s,f,t,u,dd):
        if 'p' not in st:r=s.rng;st['p']=np.c_[r.uniform(0,W,n),r.uniform(0,H*.45,n),r.uniform(0,6.28,n),r.uniform(1,2.5,n)]
        o=np.zeros((H,W),np.float32)
        for x,y,ph,sz in st['p']:cv2.circle(o,(int(x),int(y)),int(sz),max(0,math.sin(t*3+ph))*.9,-1,cv2.LINE_AA)
        return f+cv2.GaussianBlur(o,(0,0),1.2)[...,None]*(dd[...,None]<.35)
    return fx

def iris(xy_rel,t_open=.35,t_full=1.25,closing=None):
    """apertura circular (como un obturador) que deja ver la imagen"""
    def fx(s,f,t,u,dd):
        x,y=xy_rel[0]*W,xy_rel[1]*H
        if t<t_open:r=0
        elif t<t_full:k=(t-t_open)/(t_full-t_open);r=(k**1.6)*1.4*H
        else:r=1.4*H
        if closing and t>closing[0]:k=min(1,(t-closing[0])/(closing[1]-closing[0]));r=min(r,(1-k)**1.5*1.4*H)
        if r>=1.39*H:return f
        yy,xx=np.ogrid[0:H,0:W];m=np.clip((r-np.sqrt((xx-x)**2+(yy-y)**2))/18,0,1).astype(np.float32)[...,None]
        ring=np.exp(-((np.sqrt((xx-x)**2+(yy-y)**2)-r)**2)/(2*10**2)).astype(np.float32)[...,None]*(r>2)
        return f*m+ring*np.array([.1,.1,1.0],np.float32)*.9
    return fx
def glitch(times,dur=.12,amt=26):
    def fx(s,f,t,u,dd):
        if not any(t0<=t<t0+dur for t0 in times):return f
        k=int(amt*(.5+.5*math.sin(t*90)));out=f.copy()
        out[...,2]=np.roll(f[...,2],k,axis=1);out[...,0]=np.roll(f[...,0],-k,axis=1)
        for _ in range(6):
            y0=int(np.random.uniform(0,H-60));h=int(np.random.uniform(10,60));out[y0:y0+h]=np.roll(out[y0:y0+h],int(np.random.uniform(-80,80)),axis=1)
        out[::4]*=.75;return out
    return fx
def tint(col,amt):
    def fx(s,f,t,u,dd):return f*(1-amt)+f.mean(2,keepdims=True)*np.array(col[::-1],np.float32)*amt
    return fx
