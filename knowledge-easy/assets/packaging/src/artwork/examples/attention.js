// One authored example, not a layout to refill. The eye is a selective aperture.
const u=t/(data.duration||12), turn=data.beats?.['attention-turn'];
const reveal=turn===undefined?art.phase(u,.25,.62):art.phase(t,Math.max(0,turn-3),turn);
art.camera({x:960+reveal*90,y:510,zoom:1.06-reveal*.12},()=>{
  // A field of competing signals; only one gains a clear path to the observer.
  const random=art.rng(41);
  for(let i=0;i<75;i++){
    const x=160+random()*1580,y=190+random()*510,r=3+random()*5;
    ctx.globalAlpha=(.2+random()*.35)*(1-reveal*.72);
    art.ellipse(x,y,r,r,'ink');
    if(i%3===0)art.line([[x-15,y+16],[x+24,y-22]],1,'ink');
  }
  ctx.globalAlpha=1;
  ctx.save();ctx.translate(-reveal*170,0);
  art.eye(880,440,1.82,{look:Math.sin(u*5)*24,iris:'accent'});
  ctx.restore();
  const path='M1050 438 C1210 420 1250 300 1480 310';
  ctx.save();ctx.globalAlpha=reveal;art.path(path,null,'accent',10);ctx.restore();
  art.ellipse(1480,310,29*reveal,29*reveal,'accent');
  if(reveal>0){art.hatch('M1360 270 Q1500 170 1640 270 L1640 390 Q1500 470 1360 390 Z',[1360,200,300,250],{spacing:16,width:1.3,ink:'accent'});}
  // The whole field never becomes blank; the finding becomes distinct.
  art.person(1070,790,.68,{lean:-.07,left:[-80,-155],right:[78,-207]});
  art.line([[150,835],[1730,835]],2,'ink');
});
