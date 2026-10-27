/* Knowledge Easy 原创绘图工具。只使用 Canvas 2D，不包含外部绘画引擎。 */
function createArtwork(canvas, profile) {
  const W=1920,H=1080, mode=profile.engine;
  const work=canvas;
  work.width=W;work.height=H;
  const c=work.getContext('2d');
  const P={paper:'#f4eee2',ink:'#212b31',accent:'#c94c3b',secondary:'#687c69',...profile.palette};
  const clamp=(v,a=0,b=1)=>Math.max(a,Math.min(b,v));
  const mix=(a,b,p)=>a+(b-a)*p;
  const ease=p=>{p=clamp(p);return p*p*(3-2*p);};
  const phase=(t,a,b)=>ease((t-a)/Math.max(.001,b-a));
  const rng=seed=>()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296;};
  const rgb=hex=>[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16));
  function color(name='ink',alpha=1){
    if(name==='mix')name=[.8,.55,0];
    if(Array.isArray(name)){
      const inks=(profile.inks??[P.ink,P.accent,P.secondary]).map(rgb);
      return `rgba(${[0,1,2].map(k=>Math.round(255*inks.reduce((v,ink,i)=>v*(1-clamp(name[i]||0)*(1-ink[k]/255)),1))).join(',')},${clamp(alpha)})`;
    }
    const value=P[name]||name;
    return /^#[0-9a-f]{6}$/i.test(value)?`rgba(${rgb(value).join(',')},${clamp(alpha)})`:value;
  }
  const texture=document.createElement('canvas');texture.width=512;texture.height=512;
  const tc=texture.getContext('2d'),random=rng(771);
  tc.strokeStyle='rgba(65,58,45,.09)';tc.lineWidth=.6;
  for(let i=0;i<250;i++){const x=random()*512,y=random()*512;tc.beginPath();tc.moveTo(x,y);tc.lineTo(x+2+random()*5,y+(random()-.5)*2);tc.stroke();}
  function clear(){c.setTransform(1,0,0,1,0,0);c.globalAlpha=1;c.globalCompositeOperation='source-over';c.clearRect(0,0,W,H);c.fillStyle=color('paper');c.fillRect(0,0,W,H);c.lineCap='round';c.lineJoin='round';}
  function path(d,fill='ink',stroke=null,width=2){const p=new Path2D(d);if(fill){c.fillStyle=color(fill);c.fill(p);}if(stroke){c.strokeStyle=color(stroke);c.lineWidth=width;c.lineJoin='round';c.stroke(p);}return p;}
  function line(points,width=3,ink='ink',progress=1){
    if(!points.length)return;c.beginPath();c.moveTo(...points[0]);
    const end=clamp(progress)*(points.length-1),last=Math.floor(end);
    for(let i=1;i<=last;i++)c.lineTo(...points[i]);
    if(last<points.length-1)c.lineTo(mix(points[last][0],points[last+1][0],end-last),mix(points[last][1],points[last+1][1],end-last));
    c.strokeStyle=color(ink);c.lineWidth=width;c.lineCap='round';c.lineJoin='round';c.stroke();
  }
  function quadratic(a,b,d,steps=40){return Array.from({length:steps+1},(_,i)=>{const u=i/steps,v=1-u;return [v*v*a[0]+2*v*u*b[0]+u*u*d[0],v*v*a[1]+2*v*u*b[1]+u*u*d[1]];});}
  function stroke(points,width=8,ink='ink',o={}){
    const progress=clamp(o.progress??1);if(points.length<2||progress===0||width<=0)return;
    c.save();c.globalAlpha*=o.opacity??.86;
    if(mode!=='wash'){line(points,width,ink,progress);c.restore();return;}
    // Original pressure-ribbon construction: path normals define a tapered contour.
    // Pigment belongs to the stroke; there is no whole-picture dot screen.
    const lengths=points.slice(1).map((p,i)=>Math.hypot(p[0]-points[i][0],p[1]-points[i][1]));
    const total=lengths.reduce((a,b)=>a+b,0);let distance=total*progress,travel=0;
    const visible=[{p:points[0],u:0}];
    for(let i=0;i<lengths.length;i++){
      const n=lengths[i],f=n?Math.min(1,distance/n):1;travel+=n*f;
      visible.push({p:[mix(points[i][0],points[i+1][0],f),mix(points[i][1],points[i+1][1],f)],u:total?travel/total:0});
      distance-=n*f;if(f<1||distance<=0)break;
    }
    const left=[],right=[],shape=o.profile??'brush';
    visible.forEach(({p,u},i)=>{
      const a=visible[Math.max(0,i-1)].p,b=visible[Math.min(visible.length-1,i+1)].p,dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy)||1;
      const pressure=shape==='even'?.88:shape==='trunk'?1-u*.7:shape==='tip'?Math.max(.07,1-u*.92):shape==='leaf'?Math.pow(Math.max(0,Math.sin(Math.PI*u)),.65):.2+.8*Math.sin(Math.PI*(.08+u*.84));
      const radius=Math.max(.15,width*.5*pressure*(1+.055*Math.sin(u*17+(o.seed??1)*.37)));
      left.push([p[0]-dy/len*radius,p[1]+dx/len*radius]);right.push([p[0]+dy/len*radius,p[1]-dx/len*radius]);
    });
    c.beginPath();c.moveTo(...left[0]);left.slice(1).forEach(p=>c.lineTo(...p));right.reverse().forEach(p=>c.lineTo(...p));c.closePath();
    c.fillStyle=color(ink,.76);c.fill();c.strokeStyle=color(ink,.18);c.lineWidth=.8;c.stroke();
    c.clip();c.globalAlpha*=.22;line(visible.map(v=>v.p),width*.24,ink);c.restore();
  }
  function ellipse(x,y,rx,ry,ink='ink',angle=0){c.beginPath();c.ellipse(x,y,Math.max(.01,rx),Math.max(.01,ry),angle,0,Math.PI*2);c.fillStyle=color(ink);c.fill();}
  function hatch(shape,bounds,options={}){
    c.save();c.clip(typeof shape==='string'?new Path2D(shape):shape);
    const [x,y,w,h]=bounds,space=options.spacing??12,bend=options.bend??0;
    c.globalAlpha*=options.opacity??.55;c.strokeStyle=color(options.ink??'ink');c.lineWidth=options.width??1.1;
    for(let i=-h;i<w+h;i+=space){c.beginPath();c.moveTo(x+i,y+h);c.quadraticCurveTo(x+i+h*.5+bend,y+h*.4,x+i+h,y);c.stroke();}
    c.restore();
  }
  function over(fn){c.save();c.globalCompositeOperation='multiply';fn();c.restore();}
  function plate({x=0,y=0,opacity=.92}={},fn){c.save();c.translate(x,y);c.globalAlpha*=opacity;c.globalCompositeOperation='multiply';fn();c.restore();}
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
    c.save();c.translate(x,y);c.scale(scale*(o.facing===-1?-1:1),scale);c.rotate(o.lean??0);
    const coat=o.coat??'ink',skin=o.skin??'paper',edge=o.edge??'ink';
    const feet=o.feet??[[-32,82],[59,80]],left=o.left??[-92,-115],right=o.right??[92,-158];
    function ribbon(a,b,d,width,fill){
      const pts=quadratic(a,b,d,20),l=[],r=[];
      for(let i=0;i<pts.length;i++){const aa=pts[Math.max(0,i-1)],bb=pts[Math.min(pts.length-1,i+1)],dx=bb[0]-aa[0],dy=bb[1]-aa[1],n=Math.hypot(dx,dy)||1,v=width*(.56-.14*i/(pts.length-1));l.push([pts[i][0]-dy/n*v,pts[i][1]+dx/n*v]);r.push([pts[i][0]+dy/n*v,pts[i][1]-dx/n*v]);}
      path('M'+l.map(p=>p.join(' ')).join(' L')+' L'+r.reverse().map(p=>p.join(' ')).join(' L')+' Z',fill);
    }
    function palm(at,rotation){
      c.save();c.translate(...at);c.rotate(rotation);
      path('M-9 -4 L-11 -14 Q-10 -20 -7 -15 L-3 -7 L-5 -20 Q-2 -25 0 -18 L3 -7 L5 -19 Q8 -22 9 -16 L9 -3 L14 -10 Q18 -11 16 -5 L12 5 Q8 14 0 12 L-10 8 L-18 -2 Q-19 -7 -14 -5 Z',skin,edge,1.25);
      line([[-3,-2],[1,5],[6,4]],.85,edge);c.restore();
    }
    // Back leg and sleeve are drawn first, so joints read as overlapping volumes.
    ribbon([24,-70],[53,4],feet[1],32,coat);
    ribbon([-23,-71],[-42,9],feet[0],35,coat);
    for(let i=0;i<2;i++){const f=feet[i];path(`M${f[0]-16} ${f[1]-9} Q${f[0]-6} ${f[1]-15} ${f[0]+7} ${f[1]-7} L${f[0]+26} ${f[1]+5} Q${f[0]+32} ${f[1]+14} ${f[0]+17} ${f[1]+15} L${f[0]-20} ${f[1]+14} Z`,skin,edge,1.4);}
    const lshoulder=[-43,-197],rshoulder=[43,-197];
    ribbon(lshoulder,o.leftElbow??[-77,-161],left,29,coat);
    path('M-40 -217 Q-11 -233 26 -220 Q52 -214 58 -190 L48 -121 L56 -64 Q15 -47 -44 -65 L-53 -119 L-59 -178 Q-58 -203 -40 -217 Z',coat,edge,1.5);
    c.save();c.globalAlpha=.16;path('M26 -215 Q44 -153 27 -75 L55 -65 L47 -126 L55 -187 Q48 -210 26 -215 Z',skin);c.restore();
    path('M-16 -245 L-15 -216 L2 -201 L21 -215 L18 -248 Z',skin,edge,1.4);
    path('M-28 -218 L-15 -228 L2 -210 L21 -228 L35 -216 L18 -192 L1 -207 L-11 -191 Z',skin,edge,1.25);
    ribbon(rshoulder,o.rightElbow??[76,-176],right,28,coat);
    palm(left,-.65);palm(right,.45);
    c.save();c.translate(0,-266);c.rotate(o.headTilt??-.045);
    // The profile has a brow, bridge, lip and jaw; the head is not an ellipse.
    path('M-27 -21 Q-23 -46 4 -44 Q28 -42 29 -15 L27 -5 L38 9 L29 15 L31 23 Q23 43 4 42 L-14 30 L-25 9 Z',skin,edge,1.45);
    path('M-25 5 Q-43 8 -42 -6 Q-56 -13 -45 -25 Q-53 -40 -36 -46 Q-38 -64 -19 -65 Q-10 -81 6 -68 Q24 -75 29 -57 Q48 -54 40 -35 Q49 -20 33 -12 L23 -21 L18 -32 Q4 -22 -14 -25 L-20 -7 Z',edge);
    path('M-22 4 Q-38 -9 -37 7 Q-33 23 -21 17 M-32 3 Q-25 0 -26 10',skin,edge,1.15);
    line([[9,-6],[20,-3]],1.7,edge);line([[11,4],[19,6]],1.2,edge);line([[15,5],[14,10]],1.2,edge);
    line([[23,3],[23,15],[29,17]],1.05,edge);line([[20,26],[28,27]],1.05,edge);
    c.restore();
    c.save();c.globalAlpha=.62;line([[-24,-159],[-28,-110],[-14,-76]],1.4,skin);line([[18,-179],[10,-159],[10,-103]],1.2,skin);line([[-18,-31],[-23,12]],1.3,skin);c.restore();
    if(o.stripes){c.save();c.globalAlpha=.8;for(let j=0;j<6;j++)line([[-41,-178+j*17],[42,-170+j*17]],2.5,skin);c.restore();}
    c.restore();
  }
  function hand(x,y,scale=1,o={}){
    c.save();c.translate(x,y);c.scale(scale*(o.flip?-1:1),scale);c.rotate(o.angle??0);
    const d='M-190 50 L-95 25 Q-55 0 -15 -7 L131 -54 Q152 -61 157 -46 Q159 -34 143 -27 L39 17 L154 -1 Q173 -3 176 11 Q177 25 159 28 L49 44 L139 47 Q155 49 154 64 Q152 75 137 77 L42 79 L101 96 Q116 101 109 115 Q103 126 88 121 L2 106 Q-49 109 -90 80 L-190 91 Z';
    path(d,o.fill??'paper','ink',3);
    if(mode==='etch')hatch(d,[-185,-58,240,185],{spacing:15,bend:28,width:.9,opacity:.28});
    line([[-63,33],[-39,50],[-22,77]],2,'ink');c.restore();
  }
  function leaf(x,y,length=80,angle=-1,colorName='secondary',seed=3){
    if(mode==='wash'){const bend=(rng(seed)()-.5)*length*.28;stroke(quadratic([x,y],[x+Math.cos(angle)*length*.45-Math.sin(angle)*bend,y+Math.sin(angle)*length*.45+Math.cos(angle)*bend],[x+Math.cos(angle)*length,y+Math.sin(angle)*length],24),length*.27,colorName,{seed,profile:'leaf'});return;}
    c.save();c.translate(x,y);c.rotate(angle);const d=`M0 0 Q${length*.3} ${-length*.37} ${length} 0 Q${length*.3} ${length*.31} 0 0`;path(d,colorName);line([[8,0],[length-8,0]],1.5,'paper');if(mode==='etch')hatch(d,[0,-length*.4,length,length*.8],{spacing:9,width:1.3});c.restore();
  }
  function foliage(x,y,radius,o={}){
    const count=o.count??42,random=rng(o.seed??1),inks=o.colors??['secondary','ink'],growth=clamp(o.progress??1);
    for(let i=0;i<count;i++){
      const a=random()*Math.PI*2,r=Math.sqrt(random())*radius,len=(o.size??38)*(.6+random()*.8),opacity=.35+random()*.45;
      const g=phase(growth,i/count*.55,.45+i/count*.55);
      c.save();c.globalAlpha*=opacity;leaf(x+Math.cos(a)*r,y+Math.sin(a)*r*.7,len*g,a*.35-1.8,inks[i%inks.length],i+99);c.restore();
    }
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
    c.save();c.globalAlpha=.45;for(let i=0;i<19;i++){const a=i/19*Math.PI*2;line([[Math.cos(a)*35+(o.look??0),Math.sin(a)*40],[Math.cos(a)*65+(o.look??0),Math.sin(a)*72]],i%3?.8:1.5,'ink');}c.restore();
    if(mode==='etch')hatch('M-200 -10 Q0 -183 200 -10 Q0 -105 -200 -10',[-200,-145,400,155],{spacing:15,width:.8,opacity:.3});c.restore();
  }
  function finish(){
    c.save();c.setTransform(1,0,0,1,0,0);c.globalCompositeOperation='multiply';
    if(profile.texture!==false){c.globalAlpha=profile.textureStrength??.24;c.fillStyle=c.createPattern(texture,'repeat');c.fillRect(0,0,W,H);}c.restore();
  }
  return {ctx:c,W,H,profile,P,clear,color,path,line,stroke,ellipse,hatch,over,plate,camera,pose,person,hand,leaf,foliage,branch,eye,quadratic,finish,phase,ease,mix,clamp,rng};
}
