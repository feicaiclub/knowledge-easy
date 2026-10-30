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
  listen:'A',muted:false,speed:1,entries:[],panel:'marks',reviewSignature:null,reviewRequest:0,feedbackRequest:0,
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
function updateClock(){if(!S.rev)return;$('timecode').textContent=tc(S.frame);$('frameInput').value=S.frame;$('seek').value=S.frame;$('playhead').style.left=`${100*S.frame/S.rev.frames}%`;$('chapterLabel').textContent=activeChapter()?.label || 'Video preview';$('frameAccuracy').textContent=S.seeking?'Seeking…':`${fps().toFixed(fps()%1?3:0)} fps · Frame ${S.frame}`;}
function resizePictures(){for(const [screen,picture,r] of [[$('screenA'),$('pictureA'),S.rev],[$('screenB'),$('pictureB'),S.b]]){if(!r||screen.hidden)continue;const w=screen.clientWidth,h=screen.clientHeight,ratio=r.width/r.height;const width=Math.min(w,h*ratio);picture.style.width=`${width}px`;picture.style.height=`${width/ratio}px`;}}
new ResizeObserver(resizePictures).observe($('screens'));
function pause(){S.playing=false;[A,B,AA,BA].forEach(v=>v.pause());$('play').innerHTML=icon('play');$('play').setAttribute('aria-label','Play');}
function routeAudio(){const aOn=!S.muted&&(!S.compare||S.listen==='A'),bOn=!S.muted&&S.compare&&S.listen==='B';A.muted=!aOn||!!S.rev?.audio_override;AA.muted=!aOn;B.muted=!bOn||!!S.b?.audio_override;BA.muted=!bOn;$('listenA').setAttribute('aria-pressed',S.listen==='A');$('listenB').setAttribute('aria-pressed',S.listen==='B');$('mute').setAttribute('aria-pressed',S.muted);$('mute').setAttribute('aria-label',S.muted?'Unmute':'Mute');$('mute').innerHTML=icon(S.muted?'muted':'volume');}
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
async function play(){if(!S.ready)return;if(S.seeking){try{await settled();}catch(e){showToast(e.message);return;}}if(S.playing){pause();return;}if(S.frame>=S.rev.frames-1)await setFrame(0);routeAudio();const media=[A];if(S.compare&&A.currentTime<S.b.duration)media.push(B);if(S.rev.audio_override)media.push(AA);if(S.compare&&S.b.audio_override)media.push(BA);media.forEach(v=>v.playbackRate=S.speed);try{await syncOther(A.currentTime);await Promise.all(media.map(v=>v.play()));S.playing=true;$('play').innerHTML=icon('pause');$('play').setAttribute('aria-label','Pause');}catch(e){pause();showToast('Playback failed. Check the media file and try again.');}}
A.addEventListener('ended',()=>{pause();S.frame=S.rev.frames-1;updateClock();});
function loadVideo(video,url){return new Promise((resolve,reject)=>{let timer;const cleanup=()=>{clearTimeout(timer);video.removeEventListener('loadeddata',done);video.removeEventListener('error',fail);};const done=()=>{cleanup();resolve();};const fail=()=>{cleanup();reject(new Error('Could not load the film. Check the local file and browser codec support.'));};video.addEventListener('loadeddata',done,{once:true});video.addEventListener('error',fail,{once:true});timer=setTimeout(fail,15000);video.src=url;video.load();});}
function loadAudio(audio,rev){if(!rev.audio_override){audio.removeAttribute('src');audio.load();return Promise.resolve();}return new Promise((resolve,reject)=>{let timer;const done=()=>{clearTimeout(timer);audio.removeEventListener('loadedmetadata',done);audio.removeEventListener('error',fail);resolve();};const fail=()=>{clearTimeout(timer);audio.removeEventListener('loadedmetadata',done);reject(new Error('Could not load the comparison audio.'));};audio.addEventListener('loadedmetadata',done,{once:true});audio.addEventListener('error',fail,{once:true});timer=setTimeout(fail,10000);audio.src=`/media/${rev.id}/audio`;audio.load();});}
async function chooseA(id){
  if(S.loading)return;S.loading=true;pause();persistDraft();S.ready=false;
  const previousTime=S.rev?S.frame/fps():0;
  S.rev=revById(id);S.draft=null;S.selected=null;
  S.feedbackRequest++;S.reviewRequest++;S.reviewSignature=null;
  $('composer').hidden=true;$('restoreDraft').hidden=true;$('versionA').value=id;syncSelects();
  Array.from($('versionB').options).forEach(o=>o.disabled=o.value===id);
  $('feedbackVersion').textContent=S.rev.label;
  $('saveState').textContent='Feedback for this version';
  $('queuePath').textContent='Loading version feedback…';$('feedbackPath').textContent='Loading version history…';
  $('queueLink').href='/queue?revision_id='+encodeURIComponent(id);
  $('selfReview').replaceChildren(textNode('p','Loading review notes for this version…','review-empty'));
  renderFeedback();fetchFeedback();$('mediaError').hidden=true;
  try{
    await loadVideo(A,`/media/${id}/video`);await loadAudio(AA,S.rev);S.ready=true;
    S.frame=clamp(Math.round(previousTime*fps()),0,S.rev.frames-1);
    $('duration').textContent=` / ${shortTime(S.rev.duration)}`;$('frameInput').max=S.rev.frames-1;$('seek').max=S.rev.frames-1;
    $('timelineInfo').textContent=shortTime(S.rev.duration);
    $('mediaInfo').textContent=`${S.rev.width} × ${S.rev.height} · ${fps().toFixed(fps()%1?3:0)} fps · Local file`;
    $('compareBtn').disabled=S.project.revisions.length<2;renderTimeline();renderFeedback();restoreDraft(false);
    $('markLabel').textContent=S.compare?'Mark frame in A':'Mark current frame';resizePictures();routeAudio();await setFrame(S.frame);
    if(S.compare){if(S.b?.id===id)S.b=S.project.revisions.find(r=>r.id!==id);await chooseB(S.b.id);}
    loadCache(id);
  }catch(e){$('mediaError').textContent=e.message;$('mediaError').hidden=false;showToast(e.message);}
  finally{S.loading=false;}
}
async function chooseB(id){S.b=revById(id);$('versionB').value=id;syncSelects();pause();try{await loadVideo(B,`/media/${id}/video`);await loadAudio(BA,S.b);await syncOther(A.currentTime);routeAudio();resizePictures();}catch(e){showToast(e.message);}}
async function setCompare(value){pause();S.compare=value;S.listen='A';$('singleBtn').setAttribute('aria-pressed',!value);$('compareBtn').setAttribute('aria-pressed',value);$('compareBar').hidden=!value;$('screenB').hidden=!value;$('letterA').hidden=!value;$('screens').classList.toggle('comparing',value);if(value){const r=S.project.revisions.find(r=>r.id!==S.rev.id);await chooseB(r.id);$('compareNote').textContent=S.project.comparison_note || 'Compare at the same timestamp';$('compareNote').title=S.project.comparison_note || 'Compare at the same timestamp. A notice appears when the shorter version ends.';}routeAudio();$('markLabel').textContent=S.compare?'Mark frame in A':'Mark current frame';resizePictures();}
function renderTimeline(){const ruler=$('ruler'),chapters=$('chapters');ruler.replaceChildren();chapters.replaceChildren();const ticks=8*S.zoom;for(let i=0;i<=ticks;i++){const span=textNode('span',shortTime(S.rev.duration*i/ticks));span.style.left=`${100*i/ticks}%`;ruler.append(span);}for(const c of S.rev.chapters||[]){const el=textNode('button',c.label,'chapter-block');el.style.left=`${c.start/S.rev.duration*100}%`;el.style.width=`${(c.end-c.start)/S.rev.duration*100}%`;el.title=`${c.label} · ${shortTime(c.start)}`;el.onclick=()=>setFrame(Math.round(c.start*fps()));chapters.append(el);}$('timelineContent').style.width=`${S.zoom*100}%`;renderMarkers();}
async function loadCache(id){$('filmstrip').replaceChildren(textNode('span','Loading thumbnails…'));$('wave').replaceChildren();try{const result=await api(`/api/cache/${id}`);if(S.rev.id!==id)return;$('filmstrip').replaceChildren();for(const url of result.thumbnails){const img=document.createElement('img');img.src=url;img.alt='';img.draggable=false;$('filmstrip').append(img);}const peaks=result.peaks,points=[];if(peaks.length){for(let i=0;i<peaks.length;i++){points.push(`${i/(peaks.length-1)*1600},${14-peaks[i]*13}`);}for(let i=peaks.length-1;i>=0;i--)points.push(`${i/(peaks.length-1)*1600},${14+peaks[i]*13}`);const poly=document.createElementNS('http://www.w3.org/2000/svg','polygon');poly.setAttribute('points',points.join(' '));poly.setAttribute('fill','currentColor');$('wave').append(poly);}}catch(e){$('filmstrip').replaceChildren(textNode('span','Thumbnails are unavailable. Playback and comments still work.'));}}
function renderMarkers(){$('markers').replaceChildren();for(const e of S.entries.filter(e=>e.revision_id===S.rev?.id&&e.status!=='archived')){const marker=document.createElement('button');marker.className=`feedback-marker ${e.status}`;marker.style.left=`${e.start_frame/S.rev.frames*100}%`;marker.title=`${e.timecode} · ${e.note}`;marker.setAttribute('aria-label',`Jump to mark ${e.timecode}: ${e.note.slice(0,30)}`);marker.onclick=()=>openEntry(e);$('markers').append(marker);}}
function draftKey(revisionId=S.draft?.revision_id||S.rev?.id){return `lazy-review:${S.project?.feedback_path}:${revisionId}`;}
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
  $('draftHeading').textContent=S.draft.editing_id?'Edit comment':'Mark current frame';
  $('draftTime').textContent=tc(S.draft.start_frame);
  $('draftContext').textContent=`${S.rev.label} · Frame ${S.draft.start_frame}`;
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
function mergeEntries(entries){
  const merged=new Map(S.entries.map(entry=>[entry.id,entry]));let changed=false;
  for(const entry of entries){
    const previous=merged.get(entry.id);
    if(!previous||entry.seq>previous.seq||(entry.seq===previous.seq&&JSON.stringify(entry)!==JSON.stringify(previous))){merged.set(entry.id,entry);changed=true;}
  }
  if(changed)S.entries=[...merged.values()];
  return changed;
}
function finishDraftSave(submitted,entry,originalDraft){
  const key=draftKey(submitted.revision_id),current=S.draft===originalDraft;
  let latest=null;
  if(current)latest={...S.draft,note:$('noteInput').value};
  else try{latest=JSON.parse(localStorage.getItem(key)||'null');}catch{}
  if(!latest||(latest.request_id!==submitted.request_id&&latest.editing_id!==entry.id))return false;
  if(latest.note.trim()===entry.note){
    try{localStorage.removeItem(key);}catch{}
    if(current){S.draft=null;$('composer').hidden=true;$('restoreDraft').hidden=true;}
    return false;
  }
  // Text entered during the request remains an editable update to the saved mark.
  latest={...latest,editing_id:entry.id,seq:entry.seq};
  try{localStorage.setItem(key,JSON.stringify(latest));}catch{}
  if(current)S.draft=latest;
  return current;
}
async function saveFeedback(event){
  event?.preventDefault();if(!S.draft||$('saveFeedback').disabled)return;persistDraft();
  if(!S.draft.note.trim()){$('noteInput').focus();$('saveError').textContent='Describe what needs to change in this frame.';$('saveError').hidden=false;return;}
  const originalDraft=S.draft,submitted={...originalDraft};
  $('saveFeedback').disabled=true;$('saveFeedback').textContent='Saving…';$('saveError').hidden=true;
  try{
    const entry=submitted.editing_id
      ?await api('/api/feedback/update',{id:submitted.editing_id,seq:submitted.seq,note:submitted.note})
      :await api('/api/feedback',{request_id:submitted.request_id,revision_id:submitted.revision_id,start_frame:submitted.start_frame,end_frame:submitted.end_frame,note:submitted.note,category:submitted.category||'general',region:submitted.region||null});
    mergeEntries([entry]);
    const newerText=finishDraftSave(submitted,entry,originalDraft);
    if(S.rev?.id===submitted.revision_id){
      S.selected=entry.id;
      $('saveState').textContent=newerText?'Saved earlier text. Your new edits are still in the draft.':'Comment and screenshot saved.';
    }
    renderFeedback();
    showToast(newerText?'Your newer text is kept in the draft. Save again to include it.':`Saved feedback for ${revById(submitted.revision_id)?.label||submitted.revision_id}.`);
  }catch(err){$('saveError').textContent=err.message;$('saveError').hidden=false;}
  finally{$('saveFeedback').disabled=false;$('saveFeedback').innerHTML='Save <span class="key-hint">↵</span>';}
}
async function fetchFeedback(){
  const revisionId=S.rev?.id;if(!revisionId)return;
  const request=++S.feedbackRequest;
  try{
    const result=await api('/api/feedback?revision_id='+encodeURIComponent(revisionId));
    if(request!==S.feedbackRequest||S.rev?.id!==revisionId)return;
    const changed=mergeEntries(result.entries);if(changed)renderFeedback();else if(S.panel==='review')loadReview();
    if(result.queue_path)$('queuePath').textContent=result.queue_path;
    if(result.feedback_path)$('feedbackPath').textContent=result.feedback_path;
    $('connection').querySelector('span').textContent='Local review';$('connection').querySelector('i').className='dot ok';
  }catch(e){
    if(request!==S.feedbackRequest||S.rev?.id!==revisionId)return;
    $('connection').querySelector('span').textContent='Disconnected';$('connection').querySelector('i').className='dot warn';
  }
}
async function openEntry(entry){pause();if(S.rev.id!==entry.revision_id)await chooseA(entry.revision_id);S.selected=entry.id;await setFrame(entry.start_frame);renderFeedback();}
async function editEntry(entry){
  if(S.draft?.note?.trim()){showComposer();showToast('Save the current comment first.');return;}
  await openEntry(entry);S.draft={...entry,editing_id:entry.id,preview:'/'+(entry.annotated_screenshot||entry.screenshot)};showComposer();
}
async function removeEntry(entry){
  try{const updated=await api('/api/feedback/update',{id:entry.id,seq:entry.seq,status:'archived'});mergeEntries([updated]);renderFeedback();showToast('Mark removed.',async()=>{try{const restored=await api('/api/feedback/update',{id:updated.id,seq:updated.seq,status:entry.status});mergeEntries([restored]);renderFeedback();}catch(err){showToast(err.message);await fetchFeedback();}});}
  catch(err){showToast(err.message);await fetchFeedback();}
}
async function restoreEntry(entry){
  try{const updated=await api('/api/feedback/update',{id:entry.id,seq:entry.seq,status:'open'});mergeEntries([updated]);renderFeedback();showToast('Feedback restored for this version.');}
  catch(err){showToast(err.message);await fetchFeedback();}
}
function versionEntries(){
  return S.entries.filter(e=>e.revision_id===S.rev?.id)
    .sort((a,b)=>a.start_frame-b.start_frame||a.created_at.localeCompare(b.created_at));
}
function visibleEntries(){return versionEntries().filter(e=>e.status!=='archived');}
function renderFeedback(){
  if(!S.rev)return;
  const all=versionEntries(),entries=all.filter(e=>e.status!=='archived'),removed=all.filter(e=>e.status==='archived');
  $('feedbackCount').textContent=all.length;$('feedbackVersion').textContent=S.rev.label;
  const reviewing=S.panel==='review';$('selfReview').hidden=!reviewing;$('markActions').hidden=reviewing||!entries.length;
  $('restoreDraft').hidden=reviewing||!S.draft||!$('composer').hidden;
  $('feedbackList').hidden=reviewing||!all.length;$('emptyFeedback').hidden=reviewing||all.length>0||!$('composer').hidden;
  renderMarkers();if(reviewing){loadReview();return;}
  const list=$('feedbackList');
  const historyOpen=list.dataset.revisionId===S.rev.id&&!!list.querySelector('.removed-feedback')?.open;
  list.replaceChildren();list.dataset.revisionId=S.rev.id;
  const statuses={open:'Open',working:'In progress',review:'Ready to review',resolved:'Resolved',archived:'Removed'};
  function appendEntry(entry,parent){
    const item=document.createElement('article');item.className=`feedback-item${S.selected===entry.id?' selected':''}`;item.tabIndex=0;item.setAttribute('aria-label',`${entry.timecode} ${entry.note}`);
    item.onclick=()=>openEntry(entry);item.onkeydown=e=>{if(e.target===item&&(e.key==='Enter'||e.key===' ')){e.preventDefault();openEntry(entry);}};
    const top=document.createElement('div');top.className='item-top';top.append(textNode('span',entry.timecode,'item-time'),textNode('span',statuses[entry.status]||entry.status,'entry-status'));
    const actions=document.createElement('div');actions.className='mark-row-actions';
    const buttons=entry.status==='archived'?[['Restore',()=>restoreEntry(entry)]]:[['Edit',()=>editEntry(entry)],['Delete',()=>removeEntry(entry)]];
    for(const [label,fn]of buttons){const btn=textNode('button',label,'mark-text-action');btn.setAttribute('aria-label',`${label} comment at ${entry.timecode}`);btn.onclick=e=>{e.stopPropagation();fn();};actions.append(btn);}
    top.append(actions);item.append(top);
    const body=document.createElement('div');body.className='item-body';const img=document.createElement('img');img.src='/'+(entry.annotated_screenshot||entry.screenshot);img.alt=`Frame ${entry.start_frame}`;img.loading='lazy';
    body.append(img,textNode('p',entry.note));item.append(body);
    if(entry.resolution)item.append(textNode('p','Update: '+entry.resolution,'item-resolution'));
    item.append(textNode('div',`${S.rev.label} · Frame ${entry.start_frame}`,'item-meta'));parent.append(item);
  }
  for(const entry of entries)appendEntry(entry,list);
  if(removed.length){
    const history=document.createElement('details');history.className='removed-feedback';history.open=historyOpen;
    history.append(textNode('summary',`Removed feedback (${removed.length})`));
    for(const entry of removed)appendEntry(entry,history);
    list.append(history);
  }
}
async function copyFeedback(){
  const text=['Review feedback · '+S.project.title,'Revision: '+S.rev.label,...visibleEntries().map(e=>`- ${e.timecode} · Frame ${e.start_frame} · ${e.status}\n  ${e.note}${e.resolution?'\n  Update: '+e.resolution:''}\n  Screenshot: review/${e.annotated_screenshot||e.screenshot}`)].join('\n');
  try{await navigator.clipboard.writeText(text);showToast('Copied feedback for this version.');}catch{showToast('Copying is unavailable in this browser. Open the Markdown file for this version.');}
}
function addReviewText(el,text){
  const pattern=/(\d{1,2}):(\d{2})(?:\.(\d+))?/g;let last=0,match;
  while((match=pattern.exec(text))){el.append(document.createTextNode(text.slice(last,match.index)));const seconds=Number(match[1])*60+Number(match[2])+Number('0.'+(match[3]||'0'));
    if(Number(match[2])<60&&seconds<S.rev.duration){const button=textNode('button',match[0],'review-time');button.onclick=()=>setFrame(Math.round(seconds*fps()));el.append(button);}else el.append(document.createTextNode(match[0]));last=pattern.lastIndex;}
  el.append(document.createTextNode(text.slice(last)));
}
async function loadReview(){
  const revisionId=S.rev?.id;if(!revisionId||S.panel!=='review')return;
  const request=++S.reviewRequest;
  try{
    const doc=await api('/api/review?revision_id='+encodeURIComponent(revisionId));
    if(request!==S.reviewRequest||S.rev?.id!==revisionId||S.panel!=='review')return;
    const target=$('selfReview');
    if(!doc.found){S.reviewSignature=null;target.replaceChildren(textNode('p','No review notes are attached to this version yet.','review-empty'));return;}
    const signature=revisionId+':'+doc.path+':'+doc.mtime;
    if(S.reviewSignature===signature&&target.childElementCount)return;
    S.reviewSignature=signature;target.replaceChildren();
    target.append(textNode('h2',doc.title||'Review'),textNode('div',doc.path,'review-source'));
    for(const block of doc.text.split(/\n\s*\n/)){
      const trimmed=block.trim();if(!trimmed)continue;let el;
      if(/^#{1,6}\s/.test(trimmed)){el=document.createElement('h3');el.textContent=trimmed.replace(/^#{1,6}\s+/,'');}
      else{el=document.createElement('p');addReviewText(el,trimmed);}target.append(el);
    }
  }catch(e){
    if(request===S.reviewRequest&&S.rev?.id===revisionId&&S.panel==='review')$('selfReview').replaceChildren(textNode('p','Could not load review notes: '+e.message,'review-empty'));
  }
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
  $('focusBtn').onclick=()=>{const focused=$('app').classList.toggle('focus-mode');$('focusBtn').setAttribute('aria-pressed',focused);$('focusBtn').setAttribute('aria-label',focused?'Exit focus mode':'Focus mode');resizePictures();};
  document.addEventListener('keydown',e=>{if(document.querySelector('dialog[open]'))return;const input=e.target.closest('input,textarea,select,[contenteditable]');if(e.key==='Escape'){if(!$('composer').hidden)closeComposer();return;}if(input||e.ctrlKey||e.metaKey||e.altKey||selectMenu)return;
    const key=e.key.toLowerCase();if(key===' '){e.preventDefault();play();}else if(key==='arrowleft'||key==='arrowright'){e.preventDefault();setFrame((S.pending??S.frame)+(key==='arrowright'?1:-1)*(e.shiftKey?Math.round(fps()):1));}else if(key==='m'){e.preventDefault();mark();}else if(key==='?')$('helpDialog').showModal();});
  document.addEventListener('visibilitychange',()=>{if(document.hidden)pause();});
}
async function checkVersions(){try{const fresh=await api('/api/project');const additions=fresh.revisions.filter(r=>!S.project.revisions.some(old=>old.id===r.id));S.project.token=fresh.token;if(additions.length){S.project=fresh;for(const r of additions)for(const id of ['versionA','versionB']){const option=document.createElement('option');option.value=r.id;option.textContent=r.label;$(id).append(option);}$('compareBtn').disabled=S.project.revisions.length<2;showToast('New versions are available in the version menu. Existing marks still point to their original frames.');}}catch{}}
async function init(){try{S.project=await api('/api/project');$('projectTitle').textContent=S.project.title;document.title=`${S.project.title} · Lazy Studio`;$('queuePath').textContent=S.project.queue_path;$('feedbackPath').textContent=S.project.feedback_path;for(const r of S.project.revisions){for(const id of ['versionA','versionB']){const option=document.createElement('option');option.value=r.id;option.textContent=r.label;$(id).append(option);}}S.b=S.project.revisions.find(r=>r.id!==S.project.current_revision)||S.project.revisions[0];bind();initSelects();await chooseA(S.project.current_revision);await fetchFeedback();if(A.requestVideoFrameCallback)A.requestVideoFrameCallback(monitorFrame);tick();setInterval(fetchFeedback,6000);setInterval(checkVersions,12000);}catch(err){$('projectTitle').textContent='Lazy Studio could not open this project.';$('mediaError').textContent=err.message;$('mediaError').hidden=false;showToast(err.message);}}
init();
