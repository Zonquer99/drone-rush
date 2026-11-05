import sys,json,numpy as np,subprocess
sys.path.insert(0,'/tmp/claude-0/s/vid')
from synth import SR,lp,hp,bp,write,rng
T='/tmp/claude-0/s/trailer/';M=json.load(open(T+'marks.json'))
dur=float(sys.argv[1]);n=int(dur*SR);x=np.zeros(n)
def add(t,sig,g=1.0):
    i=int(t*SR);j=min(n,i+len(sig));
    if 0<=i<n:x[i:j]+=sig[:j-i]*g
def whoosh(d=.7,up=True):
    k=int(d*SR);tt=np.arange(k)/SR;e=np.sin(np.pi*tt/d)**2;s=rng.normal(0,1,k)
    lo=bp(s,300,3000)*e;return lo*.6
def impact(d=1.8):
    k=int(d*SR);tt=np.arange(k)/SR;boom=np.sin(2*np.pi*np.cumsum(38+70*np.exp(-tt/.07))/SR)*np.exp(-tt/.5);cr=hp(rng.normal(0,1,k),3000)*np.exp(-tt/.35)*.25
    return boom+cr
def thunder(d=2.2):
    k=int(d*SR);tt=np.arange(k)/SR;s=lp(rng.normal(0,1,k),500)*np.exp(-tt/.8)*(1+.6*np.sin(tt*23));cr=hp(rng.normal(0,1,k),1500)*np.exp(-tt/.12)*.5
    return (s*2.2+cr)
def motor(d=2.5):
    k=int(d*SR);tt=np.arange(k)/SR;f=120+260*(tt/d)**.7;ph=2*np.pi*np.cumsum(f)/SR
    s=(np.sin(ph)+.5*np.sin(2*ph)+.3*np.sin(3*ph))*.25+bp(rng.normal(0,1,k),800,4000)*.08;return s*np.minimum(1,tt/.4)
def rumble(d=3.0):
    k=int(d*SR);tt=np.arange(k)/SR;s=lp(rng.normal(0,1,k),120)*3+np.sin(2*np.pi*42*tt)*.5;return s*np.minimum(1,tt/1.0)*np.exp(-np.maximum(0,tt-2.2)/0.5)
add(M['s2']+.05,motor(2.5),.8)
for k in ['g1','g2','g3','g4a','g4b','g4c','g5']:add(M[k]-.35,whoosh(.6),.9)
for k in ['s3','s4','s5','g1','end']:add(M[k],impact(),.9)
for t0 in [.15,1.3,2.1]:add(M['s3']+t0,thunder(),.8)
add(M['s4'],rumble(3.0),.9)
add(M['s1']+.0,lp(rng.normal(0,1,int(3.5*SR)),300)*np.linspace(0,1,int(3.5*SR))*.4,1)   # aire de amanecer
x=np.tanh(x*.9);x=x/(np.abs(x).max()+1e-9)*.8
write(T+'sfx.wav',x)
