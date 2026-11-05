import sys,json,numpy as np
sys.path.insert(0,'/tmp/claude-0/s/vid')
from synth import SR,lp,hp,bp,write,rng
which=sys.argv[1];dur=float(sys.argv[2]);T='/tmp/claude-0/s/trailer/';M=json.load(open(T+f'marks_{which}.json'))
n=int(dur*SR);x=np.zeros(n)
def add(t,sig,g=1.0):
    i=int(t*SR);j=min(n,i+len(sig))
    if 0<=i<n and j>i:x[i:j]+=sig[:j-i]*g
tt_=lambda d:np.arange(int(d*SR))/SR
def whoosh(d=.6):t=tt_(d);return bp(rng.normal(0,1,len(t)),300,3000)*np.sin(np.pi*t/d)**2*.6
def impact(d=1.8):t=tt_(d);return np.sin(2*np.pi*np.cumsum(38+70*np.exp(-t/.07))/SR)*np.exp(-t/.5)+hp(rng.normal(0,1,len(t)),3000)*np.exp(-t/.35)*.25
def heart(d=.5):t=tt_(d);return np.sin(2*np.pi*55*t)*np.exp(-t/.09)*1.2
def braam(d=2.6,f=55):
    t=tt_(d);s=sum(np.sign(np.sin(2*np.pi*f*(1+k*.006)*t))*.25+((t*f*(1+k*.004))%1-.5)*.5 for k in range(-2,3))
    return np.tanh(lp(s,600)*1.5)*np.minimum(1,t/.08)*np.exp(-np.maximum(0,t-1.6)/.6)*.7
def shutter(d=.9):t=tt_(d);s=hp(rng.normal(0,1,len(t)),1500)*np.exp(-t/.25)*.3;
def clicks(d=.9):
    t=tt_(d);s=np.zeros(len(t))
    for k in range(9):
        i=int((.04+k*.06)*SR)
        if i+300>len(t):break
        s[i:i+300]+=hp(rng.normal(0,1,300),2500)*np.exp(-np.arange(300)/60)
    return s*.8+bp(rng.normal(0,1,len(t)),200,1200)*np.minimum(1,t/.6)*.35
def glitchs(d=.15):t=tt_(d);return np.sign(np.sin(2*np.pi*(900+rng.uniform(0,600))*t))*.35*(rng.random(len(t))>.3)
def rumble(d=3.0):t=tt_(d);return (lp(rng.normal(0,1,len(t)),120)*3+np.sin(2*np.pi*42*t)*.5)*np.minimum(1,t/1.0)*np.exp(-np.maximum(0,t-d+.8)/.4)
def pew(d=.18,f0=1400):t=tt_(d);return np.sin(2*np.pi*np.cumsum(f0*np.exp(-t/.06)+200)/SR)*np.exp(-t/.08)*.35
def alarm(d=1.4):t=tt_(d);f=600+300*(np.sin(2*np.pi*2.5*t)>0);return np.sign(np.sin(2*np.pi*np.cumsum(f)/SR))*.12*np.minimum(1,t/.1)*np.exp(-np.maximum(0,t-1.1)/.2)
if which=='v5':
    for k in range(2):add(.0+k*.3,heart(),.9)
    add(M['eye1']+.1,clicks(.6),1);add(M['eye1']+.65,braam(2.0,49),1);add(M['eye1']+.7,glitchs(),1);add(M['eye1']+1.4,glitchs(),1)
    add(M['boss'],impact(),1);add(M['boss'],rumble(1.2),.8)
    add(M['g']-.35,whoosh(),.9);add(M['g']+.1,alarm(),.8)
    g=M['g']
    for s in np.arange(1.2,7.6,.42):add(g+s,pew(),.8)
    for s in [2.6,4.9,7.0]:add(g+s,impact(1.0),.45)
    add(g+7.75,impact(),1.0)
    add(M['eye2'],braam(1.5,44),1);[add(M['eye2']+s,glitchs(),1) for s in [0,.35,.7,1.0]]
    add(M['end'],impact(),1)
else:
    add(.2,rumble(3.2),1);add(.8,braam(2.6,41),1.0)
    add(M['m2'],braam(2.2,55),1);add(M['m2'],impact(),.9);add(M['m2']+.6,impact(1.2),.5);add(M['m2']+1.4,impact(1.2),.5)
    add(M['g']-.35,whoosh(),.9);add(M['g']+.1,alarm(),.8)
    g=M['g']
    for s in np.arange(1.6,8.0,.6):add(g+s,pew(.16,1700),.7)
    add(g+8.33,impact(),1.0)
    add(M['sp']-.3,whoosh(),.8);add(M['sp'],impact(),.7);add(M['end'],braam(2.0,41),.9)
x=np.tanh(x*.9);x=x/(np.abs(x).max()+1e-9)*.85
write(T+f'sfx_{which}.wav',x)
