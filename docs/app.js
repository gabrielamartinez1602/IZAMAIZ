const video=document.querySelector('#journey');
const toggle=document.querySelector('#menu-toggle'),menu=document.querySelector('#menu');
const subtitles=document.querySelector('#subtitles'),box=document.querySelector('#subtitle');
let captionsOn=false,cues=[],awaitingAudioGesture=false;
fetch('assets/subtitles-en.json?v=43').then(r=>{if(!r.ok)throw new Error('captions');return r.json();}).then(data=>{cues=data;renderCaption();}).catch(()=>{const track=video.textTracks[0];if(track)track.mode='hidden';});
function menuState(open){menu.hidden=!open;toggle.setAttribute('aria-expanded',String(open));toggle.setAttribute('aria-label',open?'Cerrar menú':'Abrir menú');}
toggle.addEventListener('click',()=>menuState(menu.hidden));
document.addEventListener('click',e=>{if(!e.target.closest('.menu-wrap'))menuState(false);});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){menuState(false);toggle.focus();}});
document.querySelector('#restart').addEventListener('click',()=>{video.currentTime=0;renderCaption();video.play().catch(()=>{});menuState(false);});
function renderCaption(){let cue=cues.find(c=>video.currentTime>=c.start&&video.currentTime<c.end);if(!cue&&video.textTracks[0]?.activeCues?.length)cue=video.textTracks[0].activeCues[0];box.hidden=!captionsOn||!cue;box.querySelector('span').textContent=cue?.text||'';}
subtitles.addEventListener('click',()=>{captionsOn=!captionsOn;subtitles.setAttribute('aria-pressed',String(captionsOn));renderCaption();});
const track=video.textTracks[0];if(track){track.mode='hidden';track.addEventListener('cuechange',renderCaption);}
video.addEventListener('timeupdate',renderCaption);video.addEventListener('seeked',renderCaption);
function playback(){if(awaitingAudioGesture){activateAudio();return;}if(video.paused)video.play().catch(()=>{});else video.pause();}
video.addEventListener('click',playback);video.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'){e.preventDefault();playback();}});
function activateAudio(){awaitingAudioGesture=false;video.muted=false;video.volume=1;video.play().catch(()=>{});}
document.addEventListener('click',e=>{if(awaitingAudioGesture&&!e.target.closest('#journey'))activateAudio();});
video.muted=false;video.volume=1;
if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){video.autoplay=false;video.pause();}else{
video.play().catch(error=>{if(error.name!=='NotAllowedError')return;awaitingAudioGesture=true;video.muted=true;video.play().catch(()=>{});});
}
