import sys,os,shutil,subprocess,math,cv2,numpy as np
sys.path.insert(0,'/tmp/claude-0/s/trailer/scripts')
from scene import *
from PIL import Image,ImageDraw,ImageFont,ImageFilter
T='/tmp/claude-0/s/trailer/';IMG=T+'img/';OUT=os.environ.get('OUTDIR',T+'frames_final');shutil.rmtree(OUT,ignore_errors=True);os.makedirs(OUT)
BEBAS='/root/.fonts/BebasNeue-Regular.ttf';RUSSO='/root/.fonts/RussoOne-Regular.ttf';BALOO='/root/.fonts/Baloo2[wght].ttf'
def font(p,s):
    f=ImageFont.truetype(p,s)
    try:f.set_variation_by_name('ExtraBold')
    except Exception:pass
    return f
def find_col(path,ch):
    im=cv2.imread(path).astype(np.float32);o=[0,1,2];o.remove(ch);r=im[...,ch]-(im[...,o[0]]+im[...,o[1]])/2;r=cv2.GaussianBlur(r,(0,0),im.shape[1]/60)
    y,x=np.unravel_index(np.argmax(r),r.shape);return x/im.shape[1],y/im.shape[0]
def find_red(path):
    im=cv2.imread(path).astype(np.float32);r=im[...,2]-(im[...,1]+im[...,0])/2;r=cv2.GaussianBlur(r,(0,0),im.shape[1]/60)
    y,x=np.unravel_index(np.argmax(r),r.shape);return x/im.shape[1],y/im.shape[0]
def text_layer(lines,t,t0,t1,y=.78,fnt=BEBAS,size=118,col=(255,255,255),glow=(255,180,90),track=6,sub=None):
    """devuelve imagen RGBA con el texto si t en [t0,t1]"""
    if not(t0<=t<t1):return None
    u=(t-t0)/(t1-t0);a=min(1,(t-t0)/.35,(t1-t)/.35)
    L=Image.new('RGBA',(W,H),(0,0,0,0));d=ImageDraw.Draw(L);f=font(fnt,size)
    sp=track+int(10*u)  # el texto se abre poco a poco (efecto cine)
    yy=int(H*y)
    for k,line in enumerate(lines):
        ws=[d.textlength(ch,font=f) for ch in line];tw=sum(ws)+sp*(len(line)-1);x=(W-tw)/2
        for ch,w in zip(line,ws):d.text((x,yy+k*int(size*1.05)),ch,font=f,fill=col+(255,));x+=w+sp
    if sub:
        fs=font(BALOO,46);tw=d.textlength(sub,font=fs);d.text(((W-tw)/2,yy+len(lines)*int(size*1.05)+10),sub,font=fs,fill=(255,230,170,255))
    g=L.filter(ImageFilter.GaussianBlur(18));gl=Image.new('RGBA',(W,H),glow+(0,));gl.putalpha(g.getchannel('A').point(lambda v:int(v*.9)))
    out=Image.alpha_composite(gl,L);arr=np.array(out).astype(np.float32)/255.;arr[...,3]*=a
    return arr
def over(f,layer):
    if layer is None:return f
    rgb=layer[...,:3][...,::-1];al=layer[...,3:4];return f*(1-al)+rgb*al
frames=[]  # (generador)
n=0
def put(img01,grain=True):
    global n
    if grain:img=finish(img01,n)
    else:img=(np.clip(img01,0,1)*255).astype(np.uint8)
    cv2.imwrite(f'{OUT}/f{n:05d}.jpg',img,[cv2.IMWRITE_JPEG_QUALITY,92]);n+=1
MARK={}
def ai(name,img,dur,cam,fx,texts=(),fin=0,fout=0):
    MARK[name]=n/FPS
    s=Scene(IMG+img,dur,**cam);s.fx=fx+([fade(fin,fout)] if fin or fout else [])
    for i in range(int(dur*FPS)):
        f=s.frame(i);t=i/FPS
        for tx in texts:f=over(f,text_layer(t=t,**tx))
        put(f)
def game(name,mp4,dur=None,start=0,texts=(),flash_in=.0,speed_ramp=None):
    MARK[name]=n/FPS
    cap=cv2.VideoCapture(T+mp4);cap.set(cv2.CAP_PROP_POS_FRAMES,int(start*FPS));total=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))-int(start*FPS)
    N=total if dur is None else min(total,int(dur*FPS))
    for i in range(N):
        ok,fr=cap.read()
        if not ok:break
        f=fr.astype(np.float32)/255.;t=i/FPS
        if flash_in and t<flash_in:f=f+(1-t/flash_in)*1.0
        for tx in texts:f=over(f,text_layer(t=t,**tx))
        put(f,grain=False)
def flash_frames(k=3,col=1.0):
    for i in range(k):put(np.ones((H,W,3),np.float32)*col*(1-i/k),grain=False)
