// A topographic watercolor: the terrain and camera differ from the growth study.
const u=t/(data.duration||12), turn=data.beats?.['river-turn'];
const flow=turn===undefined?art.phase(u,.06,.65):art.phase(t,.2,turn);
const meet=art.phase(u,.5,.9);
art.camera({x:920,y:525,zoom:1.13-meet*.13,angle:-.025+meet*.025},()=>{
 const land='M160 346 Q270 151 610 211 Q900 118 1150 217 Q1500 179 1708 380 Q1800 665 1450 830 Q1010 900 730 817 Q420 898 202 694 Z';
 ctx.globalAlpha=.15;art.path(land,'secondary');ctx.globalAlpha=1;
 for(let i=0;i<8;i++){
  const y=310+i*52;art.stroke(art.quadratic([290,y],[900,y-220],[1590,y+60],38),2,'secondary',{seed:20+i,profile:'even',opacity:.35});
 }
 for(const [x,y,r] of [[450,425,95],[1400,380,130],[1500,700,110],[580,704,100]])
  art.foliage(x,y,r,{count:38,size:24,seed:x+y,colors:['#728d7c','#93a58b'],progress:1});
 const left=art.quadratic([460,246],[600,550],[1010,665],46),right=art.quadratic([1465,250],[1280,490],[1010,665],46);
 art.stroke(left,32,'#4e8591',{seed:51,progress:flow,profile:'even',opacity:.8});
 art.stroke(right,24,'#6a9e9e',{seed:52,progress:flow,profile:'even',opacity:.8});
 art.stroke(art.quadratic([1010,665],[1065,775],[1230,861],32),52,'#315c6d',{seed:53,progress:meet,profile:'even',opacity:.88});
 // Fine secondary tributaries reveal a network rather than two floating lines.
 [[600,358,410,320],[732,488,585,430],[1333,392,1540,390],[1165,560,1390,571]].forEach((a,i)=>art.stroke(art.quadratic([a[0],a[1]],[a[2],a[1]],[a[2],a[3]],20),7,'#7aa3a0',{seed:80+i,progress:flow,profile:'tip',opacity:.6}));
 ctx.save();ctx.translate(1250,645);ctx.rotate(-.16);art.path('M-95 -8 L95 -8 L95 16 L-95 16 Z','accent');art.line([[-90,-20],[88,-20]],3,'ink');ctx.restore();
});
