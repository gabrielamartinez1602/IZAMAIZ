from pathlib import Path
import numpy as np,subprocess,wave,json
R=Path(__file__).resolve().parents[1];D=R/'work/revision-25';D.mkdir(exist_ok=True);import os,shutil
FF=os.environ.get('FFMPEG_BINARY') or shutil.which('ffmpeg')
if not FF: raise RuntimeError('Instala FFmpeg o define FFMPEG_BINARY.')
(R/'outputs').mkdir(exist_ok=True)
SR=48000;duration=63.5;N=round(SR*duration);rng=np.random.default_rng(842)
fx=np.zeros((N,2),np.float32);tracks={}
def noise(n,low,high):
 z=rng.normal(0,1,n);f=np.fft.rfftfreq(n,1/SR);a=np.fft.rfft(z)
 filt=(1/(1+(np.maximum(low,1)/np.maximum(f,1))**8))*(1/(1+(f/high)**8));a*=filt
 v=np.fft.irfft(a,n=n);return v/(np.sqrt(np.mean(v*v))+1e-9)
def envelope(n,fade=.15):
 e=np.ones(n);k=min(int(SR*fade),n//2)
 if k:e[:k]=np.sin(np.linspace(0,np.pi/2,k))**2;e[-k:]=np.cos(np.linspace(0,np.pi/2,k))**2
 return e
def add(name,start,v,gain=1,pan=0):
 a=int(start*SR);v=np.asarray(v,dtype=np.float32)*gain;z=np.stack([v*np.sqrt((1-pan)/2),v*np.sqrt((1+pan)/2)],axis=1)
 b=min(N,a+len(z));fx[a:b]+=z[:b-a]
 if name not in tracks:tracks[name]=np.zeros((N,2),np.float32)
 tracks[name][a:b]+=z[:b-a]
def save(path,a):
 with wave.open(str(path),'wb') as f:f.setnchannels(2);f.setsampwidth(2);f.setframerate(SR);f.writeframes((np.clip(a,-1,1)*32767).astype('<i2').tobytes())
# Quiet breeze, with irregular leaf rustling rather than a strong wind gust.
n=int(6.4*SR);t=np.arange(n)/SR
wind=noise(n,140,1900)*(.7+.17*np.sin(t*1.4)+.12*np.sin(t*3.1));rustle=noise(n,1100,6500)*(.25+.25*np.sin(t*2.3)**4)
add('01_brisa_maizales',0,(wind+.25*rustle)*envelope(n,1),.014,-.12)
# Rough stone rubbing follows each small turn of the pestle.
n=int(4.05*SR);t=np.arange(n)/SR
stone=noise(n,220,4400)*(.15+.85*np.sin(t*3.0)**4)+.13*noise(n,80,600)
add('02_molienda_piedra',19.6,stone*envelope(n,.25),.026,.10)
for j,start in enumerate([19.95,20.99,22.04,23.08]):
 n=int(.19*SR);t=np.arange(n)/SR
 tap=(np.sin(2*np.pi*390*t)*np.exp(-t*35)+.35*np.sin(2*np.pi*1140*t)*np.exp(-t*52)+.65*noise(n,180,4500)*np.exp(-t*48))*envelope(n,.004)
 add('02_molienda_piedra',start,tap,.065,.1)
# Granular powder streams, two successive transfers.
for start,length,pan in [(24.38,1.48,-.10),(32.45,2.60,-.28)]:
 n=int(length*SR);t=np.arange(n)/SR
 dust=noise(n,2200,10500)*(.65+.2*np.sin(t*15)+.1*np.sin(t*31))*envelope(n,.24)
 add('03_polvo_cayendo',start,dust,.015,pan)
# Soft electric beaters: restrained harmonics with a little mechanical air.
n=int(2.50*SR);t=np.arange(n)/SR
phase=2*np.pi*(118*t+.5*np.sin(t*5))
motor=(np.sin(phase)+.33*np.sin(phase*2)+.15*np.sin(phase*4)+.10*noise(n,700,3500))*envelope(n,.35)
add('04_batidora',34.45,motor,.027,0)
# Short viscous pours follow the five mold cavities, with pauses between them.
for j in range(5):
 start=38.0+j*.56;n=int(.43*SR);t=np.arange(n)/SR
 base=noise(n,180,1850)*(.7+.2*np.sin(t*21))
 bubbles=np.zeros(n)
 for onset in [.07,.19,.32]:
  k=int(onset*SR);m=min(int(.06*SR),n-k);tt=np.arange(m)/SR
  bubbles[k:k+m]+=.22*np.sin(2*np.pi*(480*tt-1500*tt*tt))*np.exp(-tt*62)
 add('05_mezcla_en_molde',start,(base+bubbles)*envelope(n,.07),.022,-.05+j*.025)
raw=subprocess.check_output([FF,'-v','error','-i',str(R/'source-assets/musica-ajustada.m4a'),'-f','f32le','-ac','2','-ar',str(SR),'-'])
music=np.frombuffer(raw,dtype='<f4').reshape(-1,2)[:N].copy()
if len(music)<N:music=np.pad(music,((0,N-len(music)),(0,0)))
# Small music reduction around effects keeps the added sounds gentle but audible.
activity=np.max(np.abs(fx),axis=1);duck=np.ones(N,np.float32)
for lo,hi in [(0,6.4),(19.6,25.9),(32.45,40.9)]:duck[int(lo*SR):int(hi*SR)]=.94
mix=music*duck[:,None]+fx
peak=float(np.max(np.abs(mix)));ceiling=10**(-1.5/20)
if peak>ceiling:mix*=ceiling/peak
save(D/'mezcla-final.wav',mix);save(D/'efectos-completos.wav',fx)
for name,track in tracks.items():
 positions=np.flatnonzero(np.max(np.abs(track),axis=1)>1e-7)
 save(D/(name+'.wav'),track[positions[0]:positions[-1]+1])
print(json.dumps({'duration':duration,'peak_dBFS':round(float(20*np.log10(np.max(np.abs(mix)))),2),'effects_peak_dBFS':round(float(20*np.log10(np.max(np.abs(fx)))),2),'no_clipping':bool(np.max(np.abs(mix))<1)}))
for old,new in [('drafts/izamaiz-v24-boceto.mp4','izamaiz-v25-sonido-boceto.mp4'),('docs/assets/recorrido-izamaiz.mp4','izamaiz-v25-publico.mp4')]:
 subprocess.run([FF,'-v','error','-y','-i',str(R/old),'-i',str(D/'mezcla-final.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','192k','-movflags','+faststart','-shortest',str(R/'outputs'/new)],check=True)
 subprocess.run([FF,'-v','error','-i',str(R/'outputs'/new),'-f','null','-'],check=True)
print('Videos con efectos sincronizados verificados; imagen intacta.')
