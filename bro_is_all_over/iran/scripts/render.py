import sys,asyncio,os
from playwright.async_api import async_playwright
async def main(page,out,frames):
    os.makedirs(out,exist_ok=True)
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox','--allow-file-access-from-files'])
        pg=await b.new_page(viewport={'width':1920,'height':1080})
        await pg.goto('file://'+page);await pg.wait_for_function('window.ready===true')
        for i in frames:
            await pg.evaluate(f'seek({i/30})');await pg.screenshot(path=f'{out}/{i:05d}.jpg',type='jpeg',quality=92)
        await b.close()
dur=float(sys.argv[3]);fr=[int(x) for x in sys.argv[4].split(',')] if len(sys.argv)>4 else list(range(int(dur*30)))
asyncio.run(main(sys.argv[1],sys.argv[2],fr))
