import sys
from PIL import Image
from concurrent.futures import ProcessPoolExecutor
import subscribe_safari as ss
poses=ss.load_poses('poses')
N=int((ss.START+ss.DUR)*30)+3
def one(i):
    fr=Image.new('RGBA',(1920,1080),(0,0,0,0)); ss.draw_subscribe_bro(fr,i/30,poses); fr.save(f'fr/{i:04d}.png'); return i
if __name__=='__main__':
    with ProcessPoolExecutor(6) as ex: list(ex.map(one,range(N)))
    print(N)
