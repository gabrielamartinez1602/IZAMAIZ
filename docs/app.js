const video=document.querySelector('#journey');
const toggle=document.querySelector('#menu-toggle'),menu=document.querySelector('#menu');
const subtitles=document.querySelector('#subtitles'),box=document.querySelector('#subtitle');
let captionsOn=false,cues=[],awaitingAudioGesture=false;
fetch('assets/subtitles-en.json?v=43').then(r=>{if(!r.ok)throw new Error('captions');return r.json();}).then(data=>{cues=data;renderCaption();}).catch(()=>{const track=video.textTracks[0];if(track)track.mode='hidden';});
function menuState(open){menu.hidden=!open;toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');}
toggle.addEventListener('click',()=>menuState(menu.hidden));
document.addEventListener('click',e=>{if(!e.target.closest('.menu-wrap'))menuState(false);});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){menuState(false);toggle.focus();}});
document.querySelector('#restart').addEventListener('click',()=>{video.currentTime=0;renderCaption();startVideo(true);menuState(false);});
function renderCaption(){let cue=cues.find(c=>video.currentTime>=c.start&&video.currentTime<c.end);if(!cue&&video.textTracks[0]?.activeCues?.length)cue=video.textTracks[0].activeCues[0];box.hidden=!captionsOn||!cue;box.querySelector('span').textContent=cue?.text||'';}
subtitles.addEventListener('click',()=>{captionsOn=!captionsOn;subtitles.setAttribute('aria-pressed',String(captionsOn));renderCaption();});
const track=video.textTracks[0];if(track){track.mode='hidden';track.addEventListener('cuechange',renderCaption);}
video.addEventListener('timeupdate',renderCaption);video.addEventListener('seeked',renderCaption);
let playAttempt=0,hasStarted=false,lastStartGesture=-Infinity;
function startVideo(fromGesture=false){
 const attempt=++playAttempt;
 video.muted=false;video.defaultMuted=false;video.volume=1;
 if(fromGesture)lastStartGesture=performance.now();
 try{
  const result=video.play();
  if(result&&typeof result.catch==='function')result.catch(error=>{
   if(attempt!==playAttempt||!video.paused)return;
   awaitingAudioGesture=true;
   video.dataset.playback=error.name==='NotAllowedError'?'waiting-for-touch':'waiting';
  });
 }catch(error){awaitingAudioGesture=true;}
}
video.addEventListener('playing',()=>{hasStarted=true;awaitingAudioGesture=false;video.dataset.playback='playing';});
function playback(){
 if(performance.now()-lastStartGesture<650)return;
 if(video.paused||awaitingAudioGesture)startVideo(true);else video.pause();
}
video.addEventListener('click',playback);
video.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();playback();}});
// Start within the trusted touch itself; never pause/reset after an autoplay rejection.
function touchStart(){if(video.paused&&(!hasStarted||awaitingAudioGesture))startVideo(true);}
if('PointerEvent' in window)document.addEventListener('pointerup',touchStart,{capture:true,passive:true});
else document.addEventListener('touchend',touchStart,{capture:true,passive:true});
document.addEventListener('click',()=>{if(video.paused&&(!hasStarted||awaitingAudioGesture))startVideo(true);});
video.addEventListener('canplay',()=>{if(!hasStarted&&!awaitingAudioGesture)startVideo();});
window.addEventListener('pageshow',()=>{if(!hasStarted)startVideo();});
startVideo();

// Match the actual video borders with smoothly changing surrounding colors.
const edgeCanvas=document.createElement('canvas');edgeCanvas.width=36;edgeCanvas.height=64;
const edgeContext=edgeCanvas.getContext('2d',{willReadFrequently:true});
const browserTheme=document.querySelector('meta[name="theme-color"]');
let currentTop=[52,60,43],currentBottom=[52,60,43],targetTop=currentTop.slice(),targetBottom=currentBottom.slice();
let colorFrame=null,lastColorTime=0,lastThemeTime=0;
function edgeAverage(pixels,startRow,endRow){
 const sum=[0,0,0];let count=0;
 for(let y=startRow;y<endRow;y++)for(let x=0;x<36;x++){const i=(y*36+x)*4;for(let k=0;k<3;k++)sum[k]+=pixels[i+k];count++;}
 return sum.map(v=>v/count);
}
function rgb(a){return `rgb(${a.map(Math.round).join(',')})`;}
function smoothEdges(now){
 const dt=lastColorTime?Math.min((now-lastColorTime)/1000,.12):.08;lastColorTime=now;
 const blend=1-Math.exp(-dt/.45);
 currentTop=currentTop.map((v,k)=>v+(targetTop[k]-v)*blend);
 currentBottom=currentBottom.map((v,k)=>v+(targetBottom[k]-v)*blend);
 const root=document.documentElement.style;
 root.setProperty('--edge-top',rgb(currentTop));root.setProperty('--edge-bottom',rgb(currentBottom));root.setProperty('--scene-color',rgb(currentTop));
 if(now-lastThemeTime>100){browserTheme.setAttribute('content',rgb(currentTop));lastThemeTime=now;}
 const remaining=Math.max(...currentTop.map((v,k)=>Math.abs(v-targetTop[k])),...currentBottom.map((v,k)=>Math.abs(v-targetBottom[k])));
 if(remaining>.25)colorFrame=requestAnimationFrame(smoothEdges);else{browserTheme.setAttribute('content',rgb(targetTop));colorFrame=null;lastColorTime=0;}
}
function paintSurroundings(){
 if(video.readyState<2||!edgeContext)return;
 try{
  edgeContext.drawImage(video,0,0,36,64);
  const pixels=edgeContext.getImageData(0,0,36,64).data;
  targetTop=edgeAverage(pixels,0,3);targetBottom=edgeAverage(pixels,61,64);
  if(video.currentTime>=54.1)targetTop=targetBottom=[99,23,48];
  if(colorFrame===null)colorFrame=requestAnimationFrame(smoothEdges);
 }catch(error){/* Keep the previous matching tint if a frame is not ready. */}
}
video.addEventListener('loadeddata',paintSurroundings);
video.addEventListener('seeked',paintSurroundings);
video.addEventListener('timeupdate',paintSurroundings);
video.addEventListener('ended',paintSurroundings);
