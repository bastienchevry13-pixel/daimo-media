# Usage: python3 render.py slides.json OUTDIR
import sys, json, os, zipfile
from playwright.sync_api import sync_playwright
from PIL import Image
data = json.load(open(sys.argv[1])); out = sys.argv[2]; os.makedirs(out, exist_ok=True)
here = os.path.dirname(os.path.abspath(__file__)); n = len(data['slides'])
with sync_playwright() as p:
    b = p.chromium.launch(args=['--allow-file-access-from-files'])
    for tag, h, top in [('Instagram_4x5', 1350, 0), ('TikTok_9x16', 1920, 230)]:
        pg = b.new_page(viewport={'width': 1080, 'height': 1400})
        pg.add_init_script('window.DATA=' + json.dumps(data) + ';')
        pg.goto(f'file://{here}/tpl.html?h={h}&top={top}'); pg.wait_for_function('window.READY===true', timeout=30000)
        d = f'{out}/{tag}'; os.makedirs(d, exist_ok=True)
        for i in range(1, n + 1):
            pg.locator(f'#s{i}').screenshot(path=f'{d}/{data["slug"]}_{i:02d}.png')
        with zipfile.ZipFile(f'{out}/Daimo_{data["slug"]}_{tag}.zip', 'w') as z:
            for f in sorted(os.listdir(d)): z.write(f'{d}/{f}', f)
        pg.close()
    b.close()
fs = sorted(os.listdir(f'{out}/Instagram_4x5')); w, hh = 360, 450
S = Image.new('RGB', (min(len(fs), 4) * (w + 10), ((len(fs) + 3) // 4) * (hh + 10)), (0, 0, 0))
for i, f in enumerate(fs):
    S.paste(Image.open(f'{out}/Instagram_4x5/{f}').convert('RGB').resize((w, hh)), ((i % 4) * (w + 10), (i // 4) * (hh + 10)))
S.save(f'{out}/Apercu_{data["slug"]}.jpg', quality=88)
print('ok', out)
