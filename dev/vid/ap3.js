window.__ap=function(){
  if(state!=='play'){holding=false;return}
  const sx=drone.x,sy=drone.y;let best=sy,bs=-1e9;const near=[];
  for(const o of obs){if(o.suck)continue;const[x0,x1]=obXR(o);if(o.type==='laser'){near.push([o,sx,sx]);continue}if(x1<sx-20||x0>sx+330)continue;near.push([o,x0,x1])}
  for(let y=46;y<=GY-40;y+=8){let sc=1e9;
    for(const[o,x0,x1]of near){drone.x=Math.max(x0,Math.min(x1,sx));drone.y=y;let c=clearance(o);
      if(o.type==='laser'){c=Math.abs(y-o.y)-9-droneR()}
      if(o.type==='shot'){const tt=Math.max(0,(o.x-sx)/Math.max(60,-(o.vx)));const oy=o.y;o.y+=o.vy*tt;c=clearance(o);o.y=oy}
      if(o.type==='meteor'){const tt=Math.max(0,(o.x-sx)/(speed+40));drone.y=y;const ox=o.x,oy=o.y;o.y+=o.vy*tt;c=clearance(o);o.y=oy}
      sc=Math.min(sc,c)}
    drone.x=sx;drone.y=sy;
    const s=(window.__dare&&sc<60?-Math.abs(sc-(window.__dareC||9))*1.5:Math.min(sc,60))-Math.abs(y-sy)*.04-(y>GY-80?30:0);if(s>bs){bs=s;best=y}}
  drone.x=sx;drone.y=sy;
  if(!near.length)best=window.__cruise||300;
  window.__apTarget=best;
  const inv=typeof evActive==='function'&&evActive('grav');
  const pred=drone.y+drone.vy*0.16;holding=inv?pred<best:pred>best;
};
