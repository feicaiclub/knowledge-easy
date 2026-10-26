// A living cross-section: mature foliage and hidden branching structure share one trunk.
const u=t/(data.duration||12), growth=art.phase(u,.04,.48), turn=data.beats?.['root-turn'];
const reveal=turn===undefined?art.phase(u,.38,.86):art.phase(t,turn,Math.min(data.duration-.4,turn+2.4));
art.camera({x:850,y:485+reveal*55,zoom:1.1-reveal*.13},()=>{
 ctx.globalAlpha=.11;art.path('M105 607 Q590 580 1080 614 Q1410 632 1730 606 L1730 892 L105 892 Z','accent');ctx.globalAlpha=1;
 art.stroke([[110,607],[455,597],[800,607],[1290,620],[1720,607]],8,'ink',{profile:'even',seed:7});
 // A cached grove of brush leaves is a reusable drawing technique, not an image.
 art.stroke(art.brush.qctrl(810,607,767,405,826,218,32),32,'ink',{profile:'trunk',progress:growth,seed:91});
 const limbs=[[810,493,650,350],[805,418,980,309],[802,356,691,254],[813,300,928,202]];
 limbs.forEach((a,i)=>art.stroke(art.brush.qctrl(a[0],a[1],(a[0]+a[2])/2,a[3]+50,a[2],a[3],22),15-i*2,'secondary',{profile:'tip',progress:growth,seed:100+i}));
 if(!art.foliage){art.foliage=[];art.brush.withSeed(219,()=>{
   for(const [x,y,r] of [[650,350,120],[980,309,140],[691,254,100],[928,202,110],[816,260,125]])
    art.brush.clump(art.foliage,x,y,r,58,['#446d66','#698674','#91a38b'],{l0:24,l1:56,w0:11,w1:23,a0:.4,a1:.78});
 });}
 art.brush.drawList(ctx,art.foliage,growth);
 for(let i=0;i<22;i++){
  const a=-1+i/21*2,dx=a*520,yy=760+Math.sin(i*1.7)*68;
  art.stroke(art.brush.qctrl(810,610,810+dx*.2,740,810+dx,yy,30),9-i%4,'accent',{progress:reveal,seed:30+i,profile:'tip'});
  if(reveal>.4)art.stroke(art.brush.qctrl(810+dx*.65,725,800+dx,810,830+dx*1.16,855-i%4*18,20),3.5,'accent',{progress:art.phase(reveal,.4,1),seed:80+i,profile:'tip'});
 }
 art.person(1280,604,.32,{coat:'accent',left:[-60,-121],right:[92,-190]});
});
