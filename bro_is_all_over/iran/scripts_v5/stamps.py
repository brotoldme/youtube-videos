import numpy as np
from scipy.io import wavfile
from scipy.signal import butter,lfilter
SR=44100;rng=np.random.default_rng(11)
def bp(x,lo,hi,o=2):
    b,a=butter(o,[lo/(SR/2),hi/(SR/2)],'band');return lfilter(b,a,x)
def lp(x,f):b,a=butter(2,f/(SR/2));return lfilter(b,a,x)
def env(n,a,d):t=np.arange(n)/SR;return np.minimum(t/a,1)*np.exp(-t/d)
def thump(f0,f1,d,g,n=0.4):
    N=int(n*SR);t=np.arange(N)/SR;f=f1+(f0-f1)*np.exp(-t/0.025);ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*env(N,0.002,d)*g
def noise(lo,hi,d,g,n=0.4,a=0.0015):
    N=int(n*SR);return bp(rng.normal(0,1,N),lo,hi)*env(N,a,d)*g
def ring(fs,d,g,n=0.6):
    N=int(n*SR);t=np.arange(N)/SR;return sum(np.sin(2*np.pi*f*t)*np.exp(-t/(d*(1-0.15*i)))/(i+1) for i,f in enumerate(fs))*g*np.minimum(t/0.001,1)
def room(x,d=0.12,g=0.18):
    N=int(0.35*SR);ir=rng.normal(0,1,N)*np.exp(-np.arange(N)/SR/d);ir=lp(ir,3500);ir[0]=1/g
    return np.convolve(x,ir)[:len(x)+N]*g
def at(parts,n=0.9):
    out=np.zeros(int(n*SR))
    for x,t in parts:
        i=int(t*SR);out[i:i+len(x)]+=x[:len(out)-i]
    return out
def norm(x,pk=0.85):return x/np.abs(x).max()*pk
V={}
V['A']=room(at([(noise(2500,9000,0.012,0.6),0.0),(noise(250,1400,0.045,1.0),0.002),(thump(160,85,0.07,0.9),0.002),(lp(rng.normal(0,1,int(0.08*SR)),500)*env(int(0.08*SR),0.004,0.02)*0.5,0.008)]))
V['B']=room(at([(thump(120,55,0.12,1.3,0.5),0.0),(noise(200,1000,0.06,0.9),0.0),(ring([1180,2740,4130,5600],0.09,0.22),0.003),(noise(3000,9000,0.01,0.4),0.0)]),0.16,0.22)
x=V['B'];x=x/np.abs(x).max()*0.30
wavfile.write('B_laiton_lourd.wav',SR,(x*32767).astype('<i2'));print(len(x)/SR)
