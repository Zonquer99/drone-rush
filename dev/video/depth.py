import sys,cv2,numpy as np,onnxruntime as ort
sess=None
def depth(img):
    global sess
    if sess is None: sess=ort.InferenceSession('/tmp/claude-0/s/depth/model-small.onnx',providers=['CPUExecutionProvider'])
    h,w=img.shape[:2]
    x=cv2.resize(cv2.cvtColor(img,cv2.COLOR_BGR2RGB),(256,256),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255.
    x=(x-np.array([.485,.456,.406]))/np.array([.229,.224,.225]);x=x.transpose(2,0,1)[None].astype(np.float32)
    out=sess.run(None,{sess.get_inputs()[0].name:x})[0][0]
    d=cv2.resize(out,(w,h),interpolation=cv2.INTER_CUBIC)
    d=(d-d.min())/(d.max()-d.min()+1e-6)   # 1 = cerca
    d=cv2.GaussianBlur(d,(0,0),max(2,w/200))
    return d
if __name__=='__main__':
    im=cv2.imread(sys.argv[1]);d=depth(im);cv2.imwrite(sys.argv[2],(d*255).astype(np.uint8));print(d.shape)
