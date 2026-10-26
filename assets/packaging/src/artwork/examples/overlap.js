// Same print engine, different composition and meaning: overlap creates a new result.
const u=t/(data.duration||12), turn=data.beats?.['overlap-turn'];
const join=turn===undefined?art.phase(u,.23,.65):art.phase(t,Math.max(.2,turn-3),turn);
const widen=art.phase(u,.68,.94);
art.camera({x:960,y:520,zoom:1.1-widen*.15},()=>{
 const lx=630+join*170,rx=1290-join*170;
 art.ellipse(lx,500,280,280,'ink');
 art.over(()=>art.ellipse(rx,500,280,280,'accent'));
 // Different patterned fields become visible through overprinting.
 for(let i=0;i<7;i++){
  ctx.save();ctx.beginPath();ctx.arc(lx,500,270,0,Math.PI*2);ctx.clip();
  ctx.fillStyle=art.color('paper');ctx.fillRect(lx-270,310+i*62,540,14);ctx.restore();
 }
 art.over(()=>{for(let i=0;i<7;i++)art.line([[rx-180+i*60,250],[rx-180+i*60,750]],11,'accent');});
 // The gap closes into a common bridge, grounded with figures at both ends.
 ctx.globalAlpha=join;art.path('M725 792 Q960 735 1195 792 L1195 818 Q960 774 725 818 Z','mix');ctx.globalAlpha=1;
 art.person(560,785,.43,{coat:'ink',right:[95,-175]});
 art.person(1370,785,.43,{coat:'accent',left:[-95,-175]});
 art.line([[200,850],[1720,850]],3,'ink');
});
