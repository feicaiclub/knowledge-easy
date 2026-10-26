// A different problem in the same drawing language: the limit is spatial.
const u=t/(data.duration||12), burden=art.phase(u,.1,.48), turn=data.beats?.['capacity-turn'];
const boundary=turn===undefined?art.phase(u,.53,.85):art.phase(t,turn,Math.min(data.duration-.4,turn+2.6));
art.camera({x:960,y:540,zoom:1+.08*burden-.08*boundary},()=>{
  const ground='M110 825 Q470 785 910 820 Q1390 860 1810 802 L1810 884 L110 884 Z';
  art.path(ground,'ink');
  for(let i=0;i<19;i++)art.line([[130+i*86,830],[145+i*86,876]],1.5,'paper');
  art.person(910,724,1.22,{lean:.12*burden-.1*boundary,left:[-90,-145],right:[106-45*boundary,-165-38*boundary]});
  // A hand has anticipation and a retreat; it doesn't teleport between poses.
  art.hand(1510-230*burden+240*boundary,440,1.08,{flip:true,angle:-.08});
  for(let i=0;i<5;i++){
    const arrive=art.phase(u,.1+i*.045,.3+i*.045),x=1250-i*36+180*boundary;
    ctx.save();ctx.translate(x,570-i*28);ctx.rotate(-.16+i*.07);ctx.globalAlpha=arrive;
    const paper='M-85 -60 L90 -50 L84 65 L-92 58 Z';art.path(paper,'paper','ink',2.5);
    for(let k=0;k<4;k++)art.line([[-60,-35+k*22],[55,-30+k*22]],1.3,'ink');ctx.restore();
  }
  ctx.save();ctx.globalAlpha=boundary;art.path('M590 812 C535 650 600 333 896 266 C1150 211 1263 516 1203 806',null,'accent',8);ctx.restore();
});
