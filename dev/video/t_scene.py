import sys;sys.path.insert(0,'/tmp/claude-0/s/trailer/scripts')
from scene import *
import shutil,subprocess
s=Scene('/tmp/claude-0/s/trailer/thumb1.png',3.0,z0=1.0,z1=1.18,px=.2,par=.25,warm=.4)
s.fx=[dust(),flare((.55,.33)),fade(.6,0)]
d='/tmp/claude-0/s/trailer/fr_test';shutil.rmtree(d,ignore_errors=True);os.makedirs(d)
import time;t0=time.time();s.render(d);print('secs',time.time()-t0)
subprocess.run(['ffmpeg','-y','-loglevel','error','-framerate','30','-i',d+'/f%05d.jpg','-c:v','libx264','-pix_fmt','yuv420p','-crf','20','/tmp/claude-0/s/trailer/test.mp4'])
