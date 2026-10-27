'use strict';
const $ = id => document.getElementById(id);
const ICONS = {
  play:'<path d="m8 5 11 7-11 7Z"/>', pause:'<path d="M8 5v14M16 5v14"/>',
  prev:'<path d="M6 5v14m12-14L8 12l10 7Z"/>',next:'<path d="M18 5v14M6 5l10 7-10 7Z"/>',
  comment:'<path d="M20 15a3 3 0 0 1-3 3H9l-5 3V6a3 3 0 0 1 3-3h10a3 3 0 0 1 3 3Z"/><path d="M8 8h8M8 12h5"/>',
  close:'<path d="m6 6 12 12M6 18 18 6"/>',panel:'<rect x="3" y="4" width="18" height="16" rx="3"/><path d="M15 4v16"/>',
  keyboard:'<rect x="2" y="5" width="20" height="14" rx="3"/><path d="M6 9h.01M10 9h.01M14 9h.01M18 9h.01M6 12h.01M10 12h.01M14 12h.01M18 12h.01M7 16h10"/>',
  file:'<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9Z"/><path d="M14 3v6h6M8 13h8M8 17h5"/>',
  volume:'<path d="m11 4-5 4H3v8h3l5 4Zm4 4a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14"/>',
  muted:'<path d="m11 4-5 4H3v8h3l5 4Zm5 5 5 6m0-6-5 6"/>',
  crop:'<path d="M8 3v13h13M3 8h13v13M3 3h2m14 0h2v2M3 19v2h2m14 0h2"/>',
  loop:'<path d="m17 2 4 4-4 4M3 10V8a2 2 0 0 1 2-2h16M7 22l-4-4 4-4m14 0v2a2 2 0 0 1-2 2H3"/>',
  archive:'<rect x="3" y="3" width="18" height="4" rx="1"/><path d="M5 7v13h14V7M9 11h6"/>'
};
function icon(name){return `<svg viewBox="0 0 24 24" aria-hidden="true">${ICONS[name] || ICONS.comment}</svg>`;}
document.querySelectorAll('[data-icon]').forEach(el => el.innerHTML = icon(el.dataset.icon));
const S={project:null,rev:null,b:null,frame:0,presentedFrame:0,playing:false,seeking:false,pending:null,compare:false,
  listen:'A',muted:false,speed:1,entries:[],panel:'marks',reviewSignature:null,
  draft:null,selected:null,zoom:1,ready:false,loading:false,toastTimer:null,undo:null};
const A=$('videoA'),B=$('videoB'),AA=$('audioA'),BA=$('audioB');
const fps=r=>(r || S.rev).fps_num/(r || S.rev).fps_den;
const clamp=(n,a,b)=>Math.max(a,Math.min(n,b));
function tc(frame,r=S.rev){if(!r)return '00:00:00';const sec=Math.floor(frame/fps(r)),sub=Math.round(frame-Math.ceil(sec*fps(r)-1e-7));return `${String(Math.floor(sec/60)).padStart(2,'0')}:${String(sec%60).padStart(2,'0')}:${String(sub).padStart(2,'0')}`;}
function shortTime(t){return `${Math.floor(t/60)}:${String(Math.floor(t%60)).padStart(2,'0')}`;}
function showToast(message,undo=null){$('toastText').textContent=message;S.undo=undo;$('undoBtn').hidden=!undo;$('toast').hidden=false;clearTimeout(S.toastTimer);S.toastTimer=setTimeout(()=>{$('toast').hidden=true;S.undo=null;},undo?12000:5500);}
async function api(path,data){const response=await fetch(path,data?{method:'POST',headers:{'Content-Type':'application/json','X-Review-Token':S.project.token},body:JSON.stringify(data)}:{cache:'no-store'});const value=await response.json();if(!response.ok)throw new Error(value.error || 'Request failed.');return value;}
function textNode(tag,text,cls){const el=document.createElement(tag);el.textContent=text;if(cls)el.className=cls;return el;}
function revById(id){return S.project.revisions.find(r=>r.id===id);}
function activeChapter(frame=S.frame){return S.rev?.chapters?.find(c=>c.start<=frame/fps()&&c.end>frame/fps());}
function updateClock(){if(!S.rev)return;$('timecode').textContent=tc(S.frame);$('frameInput').value=S.frame;$('seek').value=S.frame;$('playhead').style.left=`${100*S.frame/S.rev.frames}%`;$('chapterLabel').textContent=activeChapter()?.label || '视频预览';$('frameAccuracy').textContent=S.seeking?'正在定位…':`${fps().toFixed(fps()%1?3:0)} fps · 帧 ${S.frame}`;}
function resizePictures(){for(const [screen,picture,r] of [[$('screenA'),$('pictureA'),S.rev],[$('screenB'),$('pictureB'),S.b]]){if(!r||screen.hidden)continue;const w=screen.clientWidth,h=screen.clientHeight,ratio=r.width/r.height;const width=Math.min(w,h*ratio);picture.style.width=`${width}px`;picture.style.height=`${width/ratio}px`;}}
new ResizeObserver(resizePictures).observe($('screens'));
function pause(){S.playing=false;[A,B,AA,BA].forEach(v=>v.pause());$('play').innerHTML=icon('play');$('play').setAttribute('aria-label','播放');}
function routeAudio(){const aOn=!S.muted&&(!S.compare||S.listen==='A'),bOn=!S.muted&&S.compare&&S.listen==='B';A.muted=!aOn||!!S.rev?.audio_override;AA.muted=!aOn;B.muted=!bOn||!!S.b?.audio_override;BA.muted=!bOn;$('listenA').setAttribute('aria-pressed',S.listen==='A');$('listenB').setAttribute('aria-pressed',S.listen==='B');$('mute').setAttribute('aria-pressed',S.muted);$('mute').setAttribute('aria-label',S.muted?'取消静音':'静音');$('mute').innerHTML=icon(S.muted?'muted':'volume');}
function seekMedia(media,time){return new Promise((resolve,reject)=>{if(!media.src || !Number.isFinite(media.duration))return resolve();const target=clamp(time,0,Math.max(0,media.duration-.001));if(Math.abs(media.currentTime-target)<.00005&&!media.seeking)return resolve();let timer;const done=()=>{clearTimeout(timer);media.removeEventListener('seeked',done);resolve();};media.addEventListener('seeked',done,{once:true});timer=setTimeout(()=>{media.removeEventListener('seeked',done);reject(new Error('Seeking timed out. Please try again.'));},8000);media.currentTime=target;});}
async function syncOther(time){const jobs=[];if(S.compare&&S.b)jobs.push(seekMedia(B,time));if(S.rev?.audio_override)jobs.push(seekMedia(AA,time));if(S.compare&&S.b?.audio_override)jobs.push(seekMedia(BA,time));await Promise.all(jobs);$('compareEnd').hidden=!S.compare||time<(S.b?.duration||0);}
async function setFrame(frame){if(!S.ready)return;const target=clamp(Math.round(frame),0,S.rev.frames-1);if(S.seeking){S.pending=target;return;}pause();S.seeking=true;S.frame=target;updateClock();try{const time=(target+.1)/fps();await seekMedia(A,time);await syncOther(time);S.frame=target;}catch(err){showToast(err.message);}finally{S.seeking=false;updateClock();if(S.pending!==null){const next=S.pending;S.pending=null;await setFrame(next);}}}
async function settled(){let count=0;while(S.seeking&&count++<400)await new Promise(r=>setTimeout(r,20));if(S.seeking)throw new Error('The frame is still loading. Try marking it again in a moment.');}
function monitorFrame(_now,meta){S.presentedFrame=clamp(Math.round(meta.mediaTime*fps()),0,S.rev?.frames-1||0);if(S.playing&&!S.seeking){S.frame=S.presentedFrame;updateClock();}A.requestVideoFrameCallback?.(monitorFrame);}
function tick(){if(S.playing&&S.rev){if(!A.requestVideoFrameCallback){S.frame=clamp(Math.floor(A.currentTime*fps()),0,S.rev.frames-1);updateClock();}const t=A.currentTime;
  if(S.compare&&S.b){$('compareEnd').hidden=t<S.b.duration;if(t<S.b.duration-.04&&Math.abs(B.currentTime-t)>.08)B.currentTime=t;if(t>=S.b.duration)B.pause();}
  for(const [v,r,on] of [[AA,S.rev,true],[BA,S.b,S.compare]])if(on&&r?.audio_override&&Math.abs(v.currentTime-t)>.12&&t<v.duration)v.currentTime=t;
  const head=S.frame/S.rev.frames*$('timelineContent').clientWidth,scroll=$('timelineScroll');if(head<scroll.scrollLeft||head>scroll.scrollLeft+scroll.clientWidth-15)scroll.scrollLeft=Math.max(0,head-scroll.clientWidth*.15);
}requestAnimationFrame(tick);}
async function play(){if(!S.ready)return;if(S.seeking){try{await settled();}catch(e){showToast(e.message);return;}}if(S.playing){pause();return;}if(S.frame>=S.rev.frames-1)await setFrame(0);routeAudio();const media=[A];if(S.compare&&A.currentTime<S.b.duration)media.push(B);if(S.rev.audio_override)media.push(AA);if(S.compare&&S.b.audio_override)media.push(BA);media.forEach(v=>v.playbackRate=S.speed);try{await syncOther(A.currentTime);await Promise.all(media.map(v=>v.play()));S.playing=true;$('play').innerHTML=icon('pause');$('play').setAttribute('aria-label','暂停');}catch(e){pause();showToast('播放失败，请检查媒体文件后重试。');}}
A.addEventListener('ended',()=>{pause();S.frame=S.rev.frames-1;updateClock();});
function loadVideo(video,url){return new Promise((resolve,reject)=>{let timer;const cleanup=()=>{clearTimeout(timer);video.removeEventListener('loadeddata',done);video.removeEventListener('error',fail);};const done=()=>{cleanup();resolve();};const fail=()=>{cleanup();reject(new Error('Could not load the film. Check the local file and browser codec support.'));};video.addEventListener('loadeddata',done,{once:true});video.addEventListener('error',fail,{once:true});timer=setTimeout(fail,15000);video.src=url;video.load();});}
function loadAudio(audio,rev){if(!rev.audio_override){audio.removeAttribute('src');audio.load();return Promise.resolve();}return new Promise((resolve,reject)=>{let timer;const done=()=>{clearTimeout(timer);audio.removeEventListener('loadedmetadata',done);audio.removeEventListener('error',fail);resolve();};const fail=()=>{clearTimeout(timer);audio.removeEventListener('loadedmetadata',done);reject(new Error('Could not load the comparison audio.'));};audio.addEventListener('loadedmetadata',done,{once:true});audio.addEventListener('error',fail,{once:true});timer=setTimeout(fail,10000);audio.src=`/media/${rev.id}/audio`;audio.load();});}
async function chooseA(id){if(S.loading)return;S.loading=true;pause();persistDraft();S.ready=false;const previousTime=S.rev?S.frame/fps():0;S.rev=revById(id);S.draft=null;S.selected=null;$('composer').hidden=true;$('restoreDraft').hidden=true;$('versionA').value=id;syncSelects();Array.from($('versionB').options).forEach(o=>o.disabled=o.value===id);$('mediaError').hidden=true;try{await loadVideo(A,`/media/${id}/video`);await loadAudio(AA,S.rev);S.ready=true;S.frame=clamp(Math.round(previousTime*fps()),0,S.rev.frames-1);$('duration').textContent=` / ${shortTime(S.rev.duration)}`;$('frameInput').max=S.rev.frames-1;$('seek').max=S.rev.frames-1;$('timelineInfo').textContent=`${shortTime(S.rev.duration)}`;$('mediaInfo').textContent=`${S.rev.width} × ${S.rev.height} · ${fps().toFixed(fps()%1?3:0)} fps · 本地文件`;$('compareBtn').disabled=S.project.revisions.length<2;renderTimeline();renderFeedback();restoreDraft(false);$('markLabel').textContent=S.compare?'标记 A 的当前帧':'标记当前帧';resizePictures();routeAudio();await setFrame(S.frame);if(S.compare){if(S.b?.id===id){S.b=S.project.revisions.find(r=>r.id!==id);}await chooseB(S.b.id);}loadCache(id);}catch(e){$('mediaError').textContent=e.message;$('mediaError').hidden=false;showToast(e.message);}finally{S.loading=false;}}
async function chooseB(id){S.b=revById(id);$('versionB').value=id;syncSelects();pause();try{await loadVideo(B,`/media/${id}/video`);await loadAudio(BA,S.b);await syncOther(A.currentTime);routeAudio();resizePictures();}catch(e){showToast(e.message);}}
async function setCompare(value){pause();S.compare=value;S.listen='A';$('singleBtn').setAttribute('aria-pressed',!value);$('compareBtn').setAttribute('aria-pressed',value);$('compareBar').hidden=!value;$('screenB').hidden=!value;$('letterA').hidden=!value;$('screens').classList.toggle('comparing',value);if(value){const r=S.project.revisions.find(r=>r.id!==S.rev.id);await chooseB(r.id);$('compareNote').textContent=S.project.comparison_note || '按相同时间位置对比';$('compareNote').title=S.project.comparison_note || '按同一时间位置对比，较短版本结束时会显示提示。';}routeAudio();$('markLabel').textContent=S.compare?'标记 A 的当前帧':'标记当前帧';resizePictures();}
function renderTimeline(){const ruler=$('ruler'),chapters=$('chapters');ruler.replaceChildren();chapters.replaceChildren();const ticks=8*S.zoom;for(let i=0;i<=ticks;i++){const span=textNode('span',shortTime(S.rev.duration*i/ticks));span.style.left=`${100*i/ticks}%`;ruler.append(span);}for(const c of S.rev.chapters||[]){const el=textNode('button',c.label,'chapter-block');el.style.left=`${c.start/S.rev.duration*100}%`;el.style.width=`${(c.end-c.start)/S.rev.duration*100}%`;el.title=`${c.label} · ${shortTime(c.start)}`;el.onclick=()=>setFrame(Math.round(c.start*fps()));chapters.append(el);}$('timelineContent').style.width=`${S.zoom*100}%`;renderMarkers();}
async function loadCache(id){$('filmstrip').replaceChildren(textNode('span','Loading thumbnails…'));$('wave').replaceChildren();try{const result=await api(`/api/cache/${id}`);if(S.rev.id!==id)return;$('filmstrip').replaceChildren();for(const url of result.thumbnails){const img=document.createElement('img');img.src=url;img.alt='';img.draggable=false;$('filmstrip').append(img);}const peaks=result.peaks,points=[];if(peaks.length){for(let i=0;i<peaks.length;i++){points.push(`${i/(peaks.length-1)*1600},${14-peaks[i]*13}`);}for(let i=peaks.length-1;i>=0;i--)points.push(`${i/(peaks.length-1)*1600},${14+peaks[i]*13}`);const poly=document.createElementNS('http://www.w3.org/2000/svg','polygon');poly.setAttribute('points',points.join(' '));poly.setAttribute('fill','currentColor');$('wave').append(poly);}}catch(e){$('filmstrip').replaceChildren(textNode('span','Thumbnails are unavailable. Playback and comments still work.'));}}
function renderMarkers(){$('markers').replaceChildren();for(const e of S.entries.filter(e=>e.revision_id===S.rev?.id&&e.status!=='archived')){const marker=document.createElement('button');marker.className=`feedback-marker ${e.status}`;marker.style.left=`${e.start_frame/S.rev.frames*100}%`;marker.title=`${e.timecode} · ${e.note}`;marker.setAttribute('aria-label',`跳转至标记 ${e.timecode}: ${e.note.slice(0,30)}`);marker.onclick=()=>openEntry(e);$('markers').append(marker);}}
function draftKey(){return `lazy-review:${S.project?.feedback_path}:${S.rev?.id}`;}
function persistDraft(){
  if(!S.draft||$('composer').hidden)return;
  S.draft.note=$('noteInput').value;
  try{if(S.draft.note.trim())localStorage.setItem(draftKey(),JSON.stringify(S.draft));else localStorage.removeItem(draftKey());}catch{}
}
function restoreDraft(open=true){
  try{const value=JSON.parse(localStorage.getItem(draftKey())||'null');if(value?.note?.trim()){S.draft=value;$('restoreDraft').hidden=open;if(open)showComposer();}}catch{}
}
function setPanel(panel){
  if(panel==='review'){persistDraft();$('composer').hidden=true;}
  S.panel=panel;
  $('marksTab').setAttribute('aria-pressed',panel==='marks');
  $('reviewTab').setAttribute('aria-pressed',panel==='review');
  renderFeedback();
}
function showComposer(){
  S.panel='marks';$('marksTab').setAttribute('aria-pressed','true');$('reviewTab').setAttribute('aria-pressed','false');
  $('composer').hidden=false;$('restoreDraft').hidden=true;$('noteInput').value=S.draft.note||'';
  $('draftHeading').textContent=S.draft.editing_id?'修改评论':'标记当前帧';
  $('draftTime').textContent=tc(S.draft.start_frame);
  $('draftContext').textContent=`${S.rev.label} · 帧 ${S.draft.start_frame}`;
  $('draftPreview').hidden=!S.draft.preview;if(S.draft.preview)$('draftPreview').src=S.draft.preview;
  $('saveError').hidden=true;renderFeedback();$('noteInput').focus();
}
function previewFrame(){
  try{const c=document.createElement('canvas');c.width=400;c.height=Math.round(400*A.videoHeight/A.videoWidth);c.getContext('2d').drawImage(A,0,0,c.width,c.height);return c.toDataURL('image/jpeg',.75);}catch{return null;}
}
async function mark(){
  if(!S.ready)return;pause();
  try{await settled();if(S.draft?.note?.trim()){showComposer();showToast('Save this comment first. Its original frame is still selected.');return;}
    await setFrame(S.frame);
    S.draft={request_id:crypto.randomUUID(),revision_id:S.rev.id,start_frame:S.frame,end_frame:S.frame+1,note:'',category:'general',region:null,preview:previewFrame()};
    $('app').classList.remove('focus-mode');$('focusBtn').setAttribute('aria-pressed','false');
    showComposer();resizePictures();
  }catch(e){showToast(e.message);}
}
function closeComposer(){persistDraft();if(S.draft&&!S.draft.note?.trim())S.draft=null;$('composer').hidden=true;$('restoreDraft').hidden=!S.draft;renderFeedback();}
async function saveFeedback(event){
  event?.preventDefault();if(!S.draft||$('saveFeedback').disabled)return;persistDraft();
  if(!S.draft.note.trim()){$('noteInput').focus();$('saveError').textContent='请描述这个画面需要怎样修改。';$('saveError').hidden=false;return;}
  $('saveFeedback').disabled=true;$('saveFeedback').textContent='正在保存…';$('saveError').hidden=true;
  try{
    const d=S.draft;
    const entry=d.editing_id?await api('/api/feedback/update',{id:d.editing_id,seq:d.seq,note:d.note}):await api('/api/feedback',{request_id:d.request_id,revision_id:d.revision_id,start_frame:d.start_frame,end_frame:d.end_frame,note:d.note,category:d.category||'general',region:d.region||null});
    S.entries=S.entries.filter(e=>e.id!==entry.id);S.entries.push(entry);S.selected=entry.id;
    localStorage.removeItem(draftKey());S.draft=null;$('composer').hidden=true;$('restoreDraft').hidden=true;
    $('saveState').textContent='评论与截图已保存。';renderFeedback();showToast('已保存到本地反馈文件。');
  }catch(err){$('saveError').textContent=err.message;$('saveError').hidden=false;}
  finally{$('saveFeedback').disabled=false;$('saveFeedback').innerHTML='保存 <span class="key-hint">↵</span>';}
}
async function fetchFeedback(){
  try{const entries=(await api('/api/feedback')).entries;if(JSON.stringify(entries)!==JSON.stringify(S.entries)){S.entries=entries;renderFeedback();}if(S.panel==='review')loadReview();$('connection').querySelector('span').textContent='本地审片';$('connection').querySelector('i').className='dot ok';}
  catch(e){$('connection').querySelector('span').textContent='连接已断开';$('connection').querySelector('i').className='dot warn';}
}
async function openEntry(entry){pause();if(S.rev.id!==entry.revision_id)await chooseA(entry.revision_id);S.selected=entry.id;await setFrame(entry.start_frame);renderFeedback();}
async function editEntry(entry){
  if(S.draft?.note?.trim()){showComposer();showToast('Save the current comment first.');return;}
  await openEntry(entry);S.draft={...entry,editing_id:entry.id,preview:'/'+(entry.annotated_screenshot||entry.screenshot)};showComposer();
}
async function removeEntry(entry){
  try{const updated=await api('/api/feedback/update',{id:entry.id,seq:entry.seq,status:'archived'});S.entries=S.entries.map(e=>e.id===updated.id?updated:e);renderFeedback();showToast('Mark removed.',async()=>{try{const restored=await api('/api/feedback/update',{id:updated.id,seq:updated.seq,status:entry.status});S.entries=S.entries.map(e=>e.id===restored.id?restored:e);renderFeedback();}catch(err){showToast(err.message);await fetchFeedback();}});}
  catch(err){showToast(err.message);await fetchFeedback();}
}
function visibleEntries(){return S.entries.filter(e=>!['archived','resolved'].includes(e.status)).sort((a,b)=>a.start_frame-b.start_frame||a.created_at.localeCompare(b.created_at));}
function renderFeedback(){
  if(!S.rev)return;const entries=visibleEntries();$('feedbackCount').textContent=entries.length;
  const reviewing=S.panel==='review';$('selfReview').hidden=!reviewing;$('markActions').hidden=reviewing||!entries.length;
  $('restoreDraft').hidden=reviewing||!S.draft||!$('composer').hidden;
  $('feedbackList').hidden=reviewing||!entries.length;$('emptyFeedback').hidden=reviewing||entries.length>0||!$('composer').hidden;
  renderMarkers();if(reviewing){loadReview();return;}
  const list=$('feedbackList');list.replaceChildren();
  for(const entry of entries){
    const item=document.createElement('article');item.className=`feedback-item${S.selected===entry.id?' selected':''}`;item.tabIndex=0;item.setAttribute('aria-label',`${entry.timecode} ${entry.note}`);
    item.onclick=()=>openEntry(entry);item.onkeydown=e=>{if(e.target===item&&(e.key==='Enter'||e.key===' ')){e.preventDefault();openEntry(entry);}};
    const top=document.createElement('div');top.className='item-top';top.append(textNode('span',entry.timecode,'item-time'));
    const actions=document.createElement('div');actions.className='mark-row-actions';
    for(const [label,fn] of [['修改',()=>editEntry(entry)],['删除',()=>removeEntry(entry)]]){const btn=textNode('button',label,'mark-text-action');btn.setAttribute('aria-label',`${label}评论于 ${entry.timecode}`);btn.onclick=e=>{e.stopPropagation();fn();};actions.append(btn);}
    top.append(actions);item.append(top);
    const body=document.createElement('div');body.className='item-body';const img=document.createElement('img');img.src='/'+(entry.annotated_screenshot||entry.screenshot);img.alt=`Frame ${entry.start_frame}`;img.loading='lazy';
    body.append(img,textNode('p',entry.note));item.append(body,textNode('div',`${revById(entry.revision_id)?.label||entry.revision_id} · 帧 ${entry.start_frame}`,'item-meta'));list.append(item);
  }
}
async function copyFeedback(){
  const text=['Review feedback · '+S.project.title,...visibleEntries().map(e=>`- ${revById(e.revision_id)?.label||e.revision_id} · ${e.timecode} · 帧 ${e.start_frame}\n  ${e.note}\n  Screenshot: review/${e.screenshot}`)].join('\n');
  try{await navigator.clipboard.writeText(text);showToast('Copied. Paste this into the original chat.');}catch{showToast('Copying is unavailable in this browser. Your feedback is saved in the local Markdown file.');}
}
function addReviewText(el,text){
  const pattern=/(\d{1,2}):(\d{2})(?:\.(\d+))?/g;let last=0,match;
  while((match=pattern.exec(text))){el.append(document.createTextNode(text.slice(last,match.index)));const seconds=Number(match[1])*60+Number(match[2])+Number('0.'+(match[3]||'0'));
    if(Number(match[2])<60&&seconds<S.rev.duration){const button=textNode('button',match[0],'review-time');button.onclick=()=>setFrame(Math.round(seconds*fps()));el.append(button);}else el.append(document.createTextNode(match[0]));last=pattern.lastIndex;}
  el.append(document.createTextNode(text.slice(last)));
}
async function loadReview(){
  if(S.reviewLoading)return;S.reviewLoading=true;
  try{const doc=await api('/api/review');if(S.panel!=='review')return;const target=$('selfReview');
    if(!doc.found){target.replaceChildren(textNode('p','No review notes are available for this project yet.','review-empty'));return;}
    const signature=doc.path+':'+doc.mtime;if(S.reviewSignature===signature&&target.childElementCount)return;S.reviewSignature=signature;target.replaceChildren();
    target.append(textNode('h2',doc.title||'Review'),textNode('div',doc.path,'review-source'));
    for(const block of doc.text.split(/\n\s*\n/)){const trimmed=block.trim();if(!trimmed)continue;let el;
      if(/^#{1,6}\s/.test(trimmed)){el=document.createElement('h3');el.textContent=trimmed.replace(/^#{1,6}\s+/,'');}
      else{el=document.createElement('p');addReviewText(el,trimmed);}target.append(el);}
  }catch(e){if(S.panel==='review')$('selfReview').replaceChildren(textNode('p','Could not load review notes: '+e.message,'review-empty'));}
  finally{S.reviewLoading=false;}
}
function bind(){
  $('play').onclick=play;$('prevFrame').onclick=()=>setFrame((S.pending??S.frame)-1);$('nextFrame').onclick=()=>setFrame((S.pending??S.frame)+1);
  const jump=()=>{const n=Number($('frameInput').value);if(Number.isFinite(n)&&n!==S.frame)setFrame(n);};$('frameInput').onchange=jump;$('frameInput').onblur=jump;$('frameInput').onkeydown=e=>{if(e.key==='Enter'){e.preventDefault();jump();$('frameInput').blur();}};
  $('seek').oninput=e=>setFrame(Number(e.target.value));$('markBtn').onclick=mark;$('emptyMark').onclick=mark;
  $('zoom').onchange=e=>{S.zoom=Number(e.target.value);renderTimeline();updateClock();};
  $('versionA').onchange=e=>chooseA(e.target.value);$('versionB').onchange=e=>chooseB(e.target.value);$('swapBtn').onclick=()=>chooseA(S.b.id);$('singleBtn').onclick=()=>setCompare(false);$('compareBtn').onclick=()=>setCompare(true);
  $('listenA').onclick=()=>{S.listen='A';routeAudio();};$('listenB').onclick=()=>{S.listen='B';routeAudio();};$('speed').onchange=e=>{S.speed=Number(e.target.value);[A,B,AA,BA].forEach(v=>v.playbackRate=S.speed);};$('mute').onclick=()=>{S.muted=!S.muted;routeAudio();};
  $('composer').onsubmit=saveFeedback;$('noteInput').oninput=persistDraft;
  $('noteInput').onkeydown=e=>{if(e.key==='Enter'&&!e.shiftKey&&!e.isComposing&&e.keyCode!==229){e.preventDefault();e.stopPropagation();saveFeedback();}};
  $('closeDraft').onclick=closeComposer;$('restoreDraft').onclick=async()=>{restoreDraft(true);await setFrame(S.draft.start_frame);};
  $('marksTab').onclick=()=>setPanel('marks');$('reviewTab').onclick=()=>setPanel('review');$('copyFeedback').onclick=copyFeedback;
  $('undoBtn').onclick=()=>{const action=S.undo;S.undo=null;$('toast').hidden=true;action?.();};
  $('shortcutsBtn').onclick=()=>{$('helpDialog').showModal();};$('queueBtn').onclick=()=>{$('filesDialog').showModal();};document.querySelectorAll('.dialog-close').forEach(btn=>btn.onclick=()=>btn.closest('dialog').close());document.querySelectorAll('dialog').forEach(dialog=>dialog.onclick=e=>{if(e.target===dialog)dialog.close();});
  $('focusBtn').onclick=()=>{const focused=$('app').classList.toggle('focus-mode');$('focusBtn').setAttribute('aria-pressed',focused);$('focusBtn').setAttribute('aria-label',focused?'退出专注模式':'专注模式');resizePictures();};
  document.addEventListener('keydown',e=>{if(document.querySelector('dialog[open]'))return;const input=e.target.closest('input,textarea,select,[contenteditable]');if(e.key==='Escape'){if(!$('composer').hidden)closeComposer();return;}if(input||e.ctrlKey||e.metaKey||e.altKey||selectMenu)return;
    const key=e.key.toLowerCase();if(key===' '){e.preventDefault();play();}else if(key==='arrowleft'||key==='arrowright'){e.preventDefault();setFrame((S.pending??S.frame)+(key==='arrowright'?1:-1)*(e.shiftKey?Math.round(fps()):1));}else if(key==='m'){e.preventDefault();mark();}else if(key==='?')$('helpDialog').showModal();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
}
async function checkVersions(){try{const fresh=await api('/api/project');const additions=fresh.revisions.filter(r=>!S.project.revisions.some(old=>old.id===r.id));S.project.token=fresh.token;if(additions.length){S.project=fresh;for(const r of additions)for(const id of ['versionA','versionB']){const option=document.createElement('option');option.value=r.id;option.textContent=r.label;$(id).append(option);}$('compareBtn').disabled=S.project.revisions.length<2;showToast('版本菜单中已有新版本，原标记仍对应原始画面。');}}catch{}}
async function init(){try{S.project=await api('/api/project');$('projectTitle').textContent=S.project.title;document.title=`${S.project.title} · Lazy Studio`;$('queuePath').textContent=S.project.queue_path;$('feedbackPath').textContent=S.project.feedback_path;for(const r of S.project.revisions){for(const id of ['versionA','versionB']){const option=document.createElement('option');option.value=r.id;option.textContent=r.label;$(id).append(option);}}S.b=S.project.revisions.find(r=>r.id!==S.project.current_revision)||S.project.revisions[0];bind();initSelects();await chooseA(S.project.current_revision);await fetchFeedback();if(A.requestVideoFrameCallback)A.requestVideoFrameCallback(monitorFrame);tick();setInterval(fetchFeedback,6000);setInterval(checkVersions,12000);}catch(err){$('projectTitle').textContent='审片室无法打开此项目。';$('mediaError').textContent=err.message;$('mediaError').hidden=false;showToast(err.message);}}
init();
