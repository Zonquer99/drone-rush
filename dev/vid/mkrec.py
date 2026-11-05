s=open('/home/claude/drone-rush.html').read()
s=s.replace('DPR=Math.min(window.devicePixelRatio||1,2);','DPR=Math.min(window.devicePixelRatio||1,3);').replace('function frame(now){','function frame(now){if(window.__manual)return;',1)
i=s.rfind('})();\n</script>');s=s[:i]+'window.__t=c=>eval(c);\n'+s[i:]
open('/tmp/claude-0/s/vid/rec.html','w').write('<!doctype html>'+s)
