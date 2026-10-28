const video=document.querySelector('#journey');
const play=document.querySelector('#play');
const sound=document.querySelector('#sound');
function updatePlay(){play.textContent=video.paused?'Reproducir':'Pausar';play.setAttribute('aria-label',video.paused?'Reproducir recorrido':'Pausar recorrido');}
play.addEventListener('click',()=>{if(video.paused){video.play().catch(updatePlay);}else{video.pause();}});
sound.addEventListener('click',()=>{video.muted=!video.muted;sound.textContent=video.muted?'Activar sonido':'Silenciar';sound.setAttribute('aria-pressed',String(!video.muted));if(video.paused)video.play().catch(updatePlay);});
video.addEventListener('play',updatePlay);video.addEventListener('pause',updatePlay);
if(window.matchMedia('(prefers-reduced-motion: reduce)').matches){video.autoplay=false;video.pause();}
video.play().then(()=>{if(window.matchMedia('(prefers-reduced-motion: reduce)').matches)video.pause();}).catch(updatePlay);
