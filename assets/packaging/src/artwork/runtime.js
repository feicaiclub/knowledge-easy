/* Knowledge Easy: deterministic drawing tools, not a story/template engine. */
function createArtwork(canvas, profile) {
  const W=1920,H=1080, mode=profile.engine;
  const work=mode==='print'?document.createElement('canvas'):canvas;
  work.width=W;work.height=H;
  const c=work.getContext('2d',{alpha:false});
  const printer=mode==='print'?createPrintEngine().makeRiso(canvas,W,H):null;
  const brush=createBrushEngine();
  const P={paper:'#f4eee2',ink:'#212b31',accent:'#c94c3b',secondary:'#687c69',...profile.palette};
  const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
  const mix=(a,b,p)=>a+(b-a)*p;
  const ease=p=>{p=clamp(p);return p*p*(3-2*p);};
  const phase=(t,a,b)=>ease((t-a)/Math.max(.001,b-a));
  const rng=seed=>()=>{seed|=0;seed=seed+0x6D2B79F5|0;let q=Math.imul(seed^seed>>>15,1|seed);q=q+Math.imul(q^q>>>7,61|q)^q;return((q^q>>>14)>>>0)/4294967296;};
  const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
  const densities={paper:[0,0,0],ink:[1,0,0],accent:[0,1,0],secondary:[0,0,1],mix:[1,.7,0]};
  const color=(name='ink',alpha=1)=>mode==='print'?`rgb(${(Array.isArray(name)?name:(densities[name]||[1,0,0])).map(v=>Math.round(clamp(v*alpha)*255)).join(',')})`:(P[name]||name);
  const texture=document.createElement('canvas');texture.width=256;texture.height=256;
  const tc=texture.getContext('2d'),random=rng(771);
  for(let i=0;i<900;i++){tc.fillStyle=`rgba(40,33,25,${random()*.035})`;tc.fillRect(random()*256,random()*256,random()*1.8+.3,.7);}
  const cache=new Map();
  function clear(){c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';c.fillStyle=color('paper');c.fillRect(0,0,W,H);}
  function path(d,fill='ink',stroke=null,width=2){const p=new Path2D(d);if(fill){c.fillStyle=color(fill);c.fill(p);}if(stroke){c.strokeStyle=color(stroke);c.lineWidth=width;c.lineJoin='round';c.stroke(p);}return p;}
  function line(points,width=3,ink='ink',progress=1){
    if(!points.length)return;c.beginPath();c.moveTo(...points[0]);
    const end=clamp(progress)*(points.length-1),last=Math.floor(end);
    for(let i=1;i<=last;i++)c.lineTo(...points[i]);
    if(last<points.length-1)c.lineTo(mix(points[last][0],points[last+1][0],end-last),mix(points[last][1],points[last+1][1],end-last));
    c.strokeStyle=color(ink);c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.stroke();
  }
  function stroke(points,width=8,ink='ink',options={}){
    if(mode!=='wash'){line(points,width,ink,options.progress??1);return;}
    const key=JSON.stringify([points,width,ink,options.seed??1,options.profile??'brush']);
    if(!cache.has(key))brush.withSeed(options.seed??1,()=>cache.set(key,brush.mk(points,width,P[ink]||ink,{prof:options.profile??'brush',rough:.24,nb:width>7?5:0,a:options.opacity??.9})));
    brush.drawS(c,cache.get(key),options.progress??1);
  }
  function ellipse(x,y,rx,ry,ink='ink',angle=0){c.beginPath();c.ellipse(x,y,Math.max(.01,rx),Math.max(.01,ry),angle,0,Math.PI*2);c.fillStyle=color(ink);c.fill();}
  function hatch(shape,bounds,options={}){
    c.save();c.clip(typeof shape==='string'?new Path2D(shape):shape);
    const [x,y,w,h]=bounds,space=options.spacing??12,bend=options.bend??0;
    c.strokeStyle=color(options.ink??'ink');c.lineWidth=options.width??1.8;
    for(let i=-h;i<w+h;i+=space){c.beginPath();c.moveTo(x+i,y+h);c.quadraticCurveTo(x+i+h*.5+bend,y+h*.4,x+i+h,y);c.stroke();}
    c.restore();
  }
  function over(fn){c.save();if(mode==='print')c.globalCompositeOperation='lighter';else c.globalCompositeOperation='multiply';fn();c.restore();}
  function camera({x=960,y=540,zoom=1,angle=0}={},fn){c.save();c.translate(960,540);c.scale(zoom,zoom);c.rotate(angle);c.translate(-x,-y);fn();c.restore();}
  function pose(keys,t){
    if(t<=keys[0].t)return keys[0].value;if(t>=keys.at(-1).t)return keys.at(-1).value;
    let i=0;while(keys[i+1].t<t)i++;const p=phase(t,keys[i].t,keys[i+1].t);
    function blend(a,b){if(Array.isArray(a))return a.map((x,j)=>blend(x,b[j]));if(a&&typeof a==='object')return Object.fromEntries(Object.keys(a).map(k=>[k,blend(a[k],b[k])]));return mix(a,b,p);}
    return blend(keys[i].value,keys[i+1].value);
  }
  function arm(a,b,d,width=22,ink='ink'){
    c.beginPath();c.moveTo(...a);c.quadraticCurveTo(...b,...d);c.strokeStyle=color(ink);c.lineWidth=width;c.lineCap='round';c.stroke();
  }
  function person(x,y,scale=1,o={}){
    c.save();c.translate(x,y);c.scale(scale,scale);c.rotate(o.lean??0);
    const coat=o.coat??'ink',skin=o.skin??'paper';
    path('M-44 -206 Q-8 -232 38 -207 L61 -71 Q28 -35 -29 -55 L-64 -84 Z',coat);
    // Head, ear and hair form a silhouette at final viewing size.
    ellipse(0,-255,33,43,skin,-.12);ellipse(27,-254,9,13,skin);
    path('M-32 -257 Q-43 -300 -10 -306 Q26 -313 38 -274 L23 -275 Q10 -296 -22 -277 L-24 -254 Z',coat);
    line([[7,-262],[14,-259]],3,coat);path('M14 -251 L25 -245 L15 -242',null,coat,2);
    line([[-11,-224],[-8,-207],[17,-210],[14,-224]],4,skin);
    const left=o.left??[-85,-111],right=o.right??[93,-157];
    arm([-43,-194],[-80,-151],left,25,coat);arm([36,-193],[75,-185],right,25,coat);
    ellipse(...left,12,10,skin,.3);ellipse(...right,12,10,skin,-.3);
    const feet=o.feet??[[-43,80],[50,82]];
    arm([-24,-60],[-29,10],feet[0],26,coat);arm([25,-59],[38,9],feet[1],26,coat);
    path(`M${feet[0][0]-13} ${feet[0][1]-8} l-21 18 q12 9 39 0 l-2 -18 Z`,coat);
    path(`M${feet[1][0]-12} ${feet[1][1]-8} l10 18 q28 5 37 -3 l-22 -15 Z`,coat);
    if(mode==='etch'){line([[-33,-191],[-43,-105],[-17,-85]],2,'paper');for(let k=0;k<8;k++)line([[-23+k*7,-202],[-40+k*7,-97]],1.4,'paper');}
    c.restore();
  }
  function hand(x,y,scale=1,o={}){
    c.save();c.translate(x,y);c.scale(scale*(o.flip?-1:1),scale);c.rotate(o.angle??0);
    const d='M-190 50 L-95 25 Q-55 0 -15 -7 L131 -54 Q152 -61 157 -46 Q159 -34 143 -27 L39 17 L154 -1 Q173 -3 176 11 Q177 25 159 28 L49 44 L139 47 Q155 49 154 64 Q152 75 137 77 L42 79 L101 96 Q116 101 109 115 Q103 126 88 121 L2 106 Q-49 109 -90 80 L-190 91 Z';
    path(d,o.fill??'paper','ink',3);
    if(mode==='etch')hatch(d,[-185,-58,365,185],{spacing:10,bend:28,width:1.15});
    line([[-63,33],[-39,50],[-22,77]],2,'ink');c.restore();
  }
  function leaf(x,y,length=80,angle=-1,colorName='secondary',seed=3){
    if(mode==='wash'){stroke(brush.qcurve(x,y,x+Math.cos(angle)*length,y+Math.sin(angle)*length,length*.13,14),length*.3,colorName,{seed,profile:'leaf'});return;}
    c.save();c.translate(x,y);c.rotate(angle);const d=`M0 0 Q${length*.3} ${-length*.37} ${length} 0 Q${length*.3} ${length*.31} 0 0`;path(d,colorName);line([[8,0],[length-8,0]],1.5,'paper');if(mode==='etch')hatch(d,[0,-length*.4,length,length*.8],{spacing:9,width:1.3});c.restore();
  }
  function branch(x,y,scale=1,o={}){
    c.save();c.translate(x,y);c.scale(scale,scale);const growth=o.growth??1;
    stroke([[0,0],[-8,-80],[8,-160],[1,-250]],12,o.ink??'ink',{progress:growth,profile:'trunk',seed:28});
    for(let i=0;i<7;i++){const p=clamp(growth*8-i);if(p<=0)continue;let yy=-30-i*29,dir=i%2?-2.4:-.7;leaf(i%2?-3:5,yy,(61+i%3*10)*p,dir,o.leaf??'secondary',50+i);}
    c.restore();
  }
  function eye(x,y,scale=1,o={}){
    c.save();c.translate(x,y);c.scale(scale,scale);path('M-180 0 Q0 -147 180 0 Q0 132 -180 0','paper','ink',4);
    ellipse(o.look??0,0,68,76,o.iris??'accent');ellipse(o.look??0,0,24,34,'ink');ellipse((o.look??0)-17,-25,12,14,'paper');
    for(let i=0;i<24;i++){const a=i/24*Math.PI*2;line([[Math.cos(a)*35+(o.look??0),Math.sin(a)*40],[Math.cos(a)*65+(o.look??0),Math.sin(a)*72]],1,'ink');}
    if(mode==='etch')hatch('M-200 -10 Q0 -183 200 -10 Q0 -105 -200 -10',[-200,-145,400,155],{spacing:8});c.restore();
  }
  function finish(t,o={}){
    c.setTransform(1,0,0,1,0,0);
    if(printer){printer(work,{inks:(profile.inks??['#164d62','#e58c3d','#8d4361']).map(rgb),paper:rgb(P.paper),off:[[0,0],[2.3,-1.5],[-1.5,1.2]],boil:0,grain:.55,seed:0,sheet:1,...o});}
    else if(profile.texture!==false){c.globalAlpha=.65;c.fillStyle=c.createPattern(texture,'repeat');c.fillRect(0,0,W,H);c.globalAlpha=1;}
  }
  return {ctx:c,W,H,profile,P,clear,color,path,line,stroke,ellipse,hatch,over,camera,pose,person,hand,leaf,branch,eye,finish,phase,ease,mix,clamp,rng,brush};
}
