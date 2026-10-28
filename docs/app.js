const video=document.querySelector('#journey');
const subtitleButton=document.querySelector('#subtitles');
const subtitleBox=document.querySelector('#subtitle');
let captionsOn=false,cues=[];
fetch('assets/subtitles-en.json?v=43').then(response=>{
 if(!response.ok)throw new Error('Captions unavailable');
 return response.json();
}).then(data=>{cues=data;renderCaption();}).catch(()=>{});
const track=video.textTracks[0];
if(track){track.mode='hidden';track.addEventListener('cuechange',renderCaption);}
function renderCaption(){
 let cue=cues.find(c=>video.currentTime>=c.start&&video.currentTime<c.end);
 if(!cue&&track?.activeCues?.length)cue=track.activeCues[0];
 subtitleBox.hidden=!captionsOn||!cue;
 subtitleBox.querySelector('span').textContent=cue?.text||'';
}
subtitleButton.addEventListener('click',()=>{
 captionsOn=!captionsOn;
 subtitleButton.setAttribute('aria-pressed',String(captionsOn));
 renderCaption();
});
video.addEventListener('timeupdate',renderCaption);
video.addEventListener('seeked',renderCaption);
// Let the browser's own play control handle sound and playback on mobile.
