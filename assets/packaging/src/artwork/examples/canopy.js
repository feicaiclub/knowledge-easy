// One printed city: a canopy changes both shade and the person's path.
const u=t/(data.duration||12), turn=data.beats?.['canopy-turn'];
const growth=turn===undefined?art.phase(u,.22,.72):art.phase(t,turn,Math.min(data.duration-.6,turn+4));
const walk=art.phase(u,.43,.91);
ctx.fillStyle=art.color('ink',.14);ctx.fillRect(0,0,1920,750);
art.over(()=>art.ellipse(480,280,190,190,'accent'));
art.camera({x:960+walk*70,y:540,zoom:1.05-walk*.05},()=>{
 const buildings=[{x:90,w:180,h:240},{x:300,w:200,h:330},{x:535,w:180,h:260},{x:750,w:200,h:390},{x:990,w:190,h:260},{x:1400,w:330,h:310}];
 buildings.forEach((b,i)=>{const y=730-b.h;art.path(`M${b.x} 730 V${y} L${b.x+b.w} ${y-22} V730 Z`,[.66,0,0]);
  for(let yy=y+28;yy<700;yy+=42)for(let xx=b.x+20;xx<b.x+b.w-15;xx+=34){ctx.fillStyle=art.color('paper');ctx.fillRect(xx,yy,10,19);}
 });
 art.path('M0 735 L1920 700 V1080 H0 Z','paper');
 art.path('M0 806 L1920 746 L1920 850 L0 944 Z',[0,.38,0]);
 for(let i=0;i<7;i++)art.path(`M${180+i*250} 831 l118 -5 l40 43 l-118 8 Z`,'paper');
 // Broad ink shadow and an actual branching trunk make the cause visible.
 ctx.globalAlpha=growth;art.over(()=>art.ellipse(1330,825,310,55,'secondary',-.08));ctx.globalAlpha=1;
 art.line([[1310,820],[1288,620],[1250,400]],18,'ink',growth);
 art.line([[1290,610],[1430,455]],13,'ink',growth);
 art.line([[1290,570],[1110,440]],13,'ink',growth);
 [[1120,400,135,145],[1260,312,166,170],[1430,390,150,158],[1280,440,200,115]].forEach(([x,y,rx,ry],i)=>{
  const g=art.phase(growth,i*.08,.65+i*.08);art.over(()=>art.ellipse(x,y,rx*g,ry*g,i%2?'secondary':'ink'));
 });
 for(let i=0;i<8;i++)art.over(()=>art.leaf(1110+i*42,418+Math.sin(i)*50,105*growth,-1.3+i*.09,'accent'));
 art.person(700+walk*470,790,.67,{coat:'accent',left:[-74,-131],right:[79,-160],feet:[[-43+Math.sin(walk*14)*12,80],[50-Math.sin(walk*14)*12,82]]});
});
art.printOptions={grain:.56,boil:0};
