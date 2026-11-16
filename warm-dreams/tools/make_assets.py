"""Genera warm-dreams/assets.local/assets.js a partir de los packs descargados.
Uso: python3 -I tools/make_assets.py <carpeta_con_packs>
La carpeta debe tener: hero/ (kowches), bg/ (LyniaDesign), tiles/ (The Flavare), chars/ (kanomwan).
Los archivos generados NO se suben al repo (licencias: no redistribuir)."""
import sys, os, glob, base64, io, json
from PIL import Image

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), '..', 'assets.local')
os.makedirs(OUT, exist_ok=True)

def uri(im):
    b = io.BytesIO(); im.save(b, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(b.getvalue()).decode()

# ---------------------------------------------------------------- personaje
FR = os.path.join(SRC, 'hero', 'BasicPlatformerCharacter', 'Individual Sprites')
NAMES = [('Idle', 3), ('Run', 8), ('Jump', 3), ('Fall', 2), ('Land', 3)]
frames = []
for folder, n in NAMES:
    for i in range(1, n + 1):
        frames.append(Image.open(os.path.join(FR, folder, f'player{folder}{i}.png')).convert('RGBA'))

OL = (30, 24, 40, 255)
V = {
 'haru':   dict(hair=(42,33,53), shirt=((246,243,236),(197,199,216)), low='pants', pants=((46,58,94),(34,43,71)), shoe=(241,235,226), neck='scarf', bag='pack'),
 'haruB':  dict(hair=(42,33,53), shirt=((246,243,236),(197,199,216)), low='pants', pants=((46,58,94),(34,43,71)), shoe=(241,235,226), neck='scarf', bag='packback', back=1),
 'boy':    dict(hair=(92,60,42), shirt=((246,243,236),(197,199,216)), low='pants', pants=((40,44,64),(30,33,50)), shoe=(60,50,50), neck='shirt', bag='satchel'),
 'girl':   dict(hair=(70,40,56), shirt=((246,243,236),(197,199,216)), low='skirt', skirt=(42,52,102), shoe=(70,46,40), neck='sailor', ribbon=(224,69,90), long=1),
 'aoi':    dict(hair=(48,30,44), shirt=((246,243,236),(197,199,216)), low='skirt', skirt=(42,52,102), shoe=(90,58,42), neck='sailor', ribbon=(224,69,90), long=2),
 'office': dict(hair=(30,26,36), shirt=((96,100,114),(74,78,92)), low='pants', pants=((84,88,102),(64,68,82)), shoe=(40,34,34), neck='tie'),
 'granny': dict(hair=(214,210,220), shirt=((150,112,168),(118,86,134)), low='longskirt', skirt=(110,84,124), shoe=(80,56,44), neck='shirt', bun=1),
 'jogger': dict(hair=(70,46,34), shirt=((212,84,92),(166,62,72)), low='shorts', pants=((40,40,52),(30,30,40)), shoe=(240,240,240), neck='shirt'),
}
SKIN = (243,198,160); SKIN2 = (219,160,124)

def classes(f):
    cols = {}
    for c in (f.get_flattened_data() if hasattr(f,'get_flattened_data') else f.getdata()):
        if c[3]: cols[c[:3]] = cols.get(c[:3], 0) + 1
    dark = min(cols, key=sum); light = max(cols, key=sum)
    return dark, light

def paint(f, v):
    px = f.load(); W, H = f.size; dark, light = classes(f)
    bb = f.getbbox(); top = bb[1]
    rows = [x for y in range(top+4, top+11) for x in range(W) if px[x, y][3]]
    hl = min(rows) if rows else bb[0]
    out = Image.new('RGBA', (W, H)); o = out.load()
    for y in range(H):
        for x in range(W):
            c = px[x, y]
            if not c[3]: continue
            r = y - top; k = c[:3]; sh = k != light
            if k == dark:
                o[x, y] = OL; continue
            if r <= 11:
                hair = r <= 3 or (r <= 8 and x <= hl + 3) or (v.get('back') and r <= 10)
                col = v['hair'] if hair else (SKIN2 if r == 11 else SKIN)
            elif r <= 13:
                n = v['neck']
                if n == 'scarf': col = (216,65,76)
                elif n == 'sailor': col = (42,52,102)
                elif n == 'tie': col = (240,236,230) if r == 12 else v['shirt'][1 if sh else 0]
                else: col = v['shirt'][1 if sh else 0]
            elif r <= 21:
                col = v['shirt'][1 if sh else 0]
            elif r <= 28:
                lo = v['low']
                if lo == 'pants': col = v['pants'][1 if sh else 0]
                elif lo == 'skirt': col = v['skirt'] if r <= 25 else (SKIN if r <= 27 else (240,240,240))
                elif lo == 'longskirt': col = v['skirt']
                elif lo == 'shorts': col = v['pants'][1 if sh else 0] if r <= 24 else SKIN
            else:
                col = v['shoe']
            o[x, y] = col + (255,)
    # detalles
    def put(x, y, col):
        if 0 <= x < W and 0 <= y < H: o[x, y] = col
    torso = [x for y in range(top+13, top+21) for x in range(W) if px[x, y][3]]
    tl = min(torso) if torso else bb[0]; tr = max(torso) if torso else bb[2]
    if v['neck'] == 'tie':
        cx = (tl + tr) // 2 + 1
        for y in range(top+12, top+17): put(cx, y, (192,64,74,255))
    if v.get('ribbon'):
        cx = (tl + tr) // 2 + 1
        put(cx, top+13, v['ribbon']+(255,)); put(cx+1, top+13, v['ribbon']+(255,)); put(cx, top+14, v['ribbon']+(255,))
    if v.get('long'):
        L = 3 if v['long'] == 2 else 2
        for y in range(top+3, top+15+(2 if v['long'] == 2 else 0)):
            for x in range(hl - L, hl + 2):
                if 0 <= x < W and o[x, y][3] == 0: o[x, y] = v['hair'] + (255,)
            if o[hl-L-1, y][3] == 0: put(hl-L-1, y, OL)
    if v.get('bun'):
        for y in range(top-3, top+1):
            for x in range(hl+2, hl+7):
                if o[x, y][3] == 0: o[x, y] = (OL if y == top-3 or x in (hl+2, hl+6) else v['hair']+(255,))
    bag = v.get('bag')
    if bag in ('pack', 'satchel'):
        h0, h1 = (top+13, top+22) if bag == 'pack' else (top+17, top+22)
        for y in range(h0, h1):
            for x in range(tl-4, tl+1):
                if o[x, y][3] == 0 or x >= tl-1:
                    edge = y in (h0, h1-1) or x == tl-4
                    if o[x, y][3] == 0 or x < tl+1:
                        o[x, y] = OL if edge else ((212,85,63,255) if bag == 'pack' else (110,72,52,255))
    if bag == 'packback':
        cx = (tl + tr) // 2
        for y in range(top+13, top+22):
            for x in range(cx-4, cx+5):
                edge = y in (top+13, top+21) or x in (cx-4, cx+4)
                o[x, y] = OL if edge else ((212,85,63,255) if y < top+20 else (154,58,44,255))
    return out

def shift_rows(img, y0, y1, dy, dx=0):
    """copia filas [y0,y1) desplazadas"""
    out = Image.new('RGBA', img.size)
    out.paste(img.crop((0, y0, img.width, y1)), (dx, y0 + dy))
    return out

def extra_poses(idle):
    bb = idle.getbbox(); top = bb[1]; W, H = idle.size
    # agachado: quitar filas de torso inferior y muslo
    cr = Image.new('RGBA', idle.size)
    cr.alpha_composite(idle.crop((0, top+24, W, H)), (0, top+24))
    cr.alpha_composite(idle.crop((0, top, W, top+16)), (0, top+8))
    # deslizarse: torso hacia atrás, piernas hacia adelante
    sl = Image.new('RGBA', idle.size)
    sl.alpha_composite(cr.crop((0, top+24, W, H)), (3, top+24))
    sl.alpha_composite(cr.crop((0, top+8, W, top+24)), (-2, top+8+1))
    # sentado
    si = Image.new('RGBA', idle.size); s = si.load()
    up = idle.crop((0, top, W, top+22)); si.alpha_composite(up, (0, 47-16-21))
    ip = idle.load()
    tor = [x for x in range(W) if ip[x, top+18][3]]; fx = max(tor) if tor else 38
    pants = (46,58,94,255); shoe = (241,235,226,255)
    by = 47 - 16  # altura del asiento
    for x in range(fx-6, fx+6):
        for y in range(by-2, by+2):
            s[x, y] = OL if y in (by-2, by+1) else pants
    for y in range(by+1, by+9):
        for x in range(fx+2, fx+6):
            s[x, y] = OL if x in (fx+2, fx+5) else pants
    for x in range(fx+2, fx+9):
        for y in (by+9, by+10, by+11):
            s[x, y] = OL if y == by+11 or x == fx+8 or y == by+9 and x > fx+5 else shoe
    return cr, sl, si

CW, CH, CX0, CY0 = 40, 40, 12, 8
order = list(V.keys())
NF = len(frames) + 3
atlas = Image.new('RGBA', (CW * NF, CH * len(order)))
for row, name in enumerate(order):
    painted = [paint(f, V[name]) for f in frames]
    painted += list(extra_poses(painted[0]))
    for i, p in enumerate(painted):
        atlas.alpha_composite(p.crop((CX0, CY0, CX0+CW, CY0+CH)), (i*CW, row*CH))
atlas.save(os.path.join(OUT, 'preview_atlas.png'))
meta = dict(cw=CW, ch=CH, ox=20, oy=39, rows={n: i for i, n in enumerate(order)},
            frames=dict(idle=[0,1,2], run=list(range(3,11)), jump=[11,12,13], fall=[14,15], land=[16,17,18], crouch=[19], slide=[20], sit=[21]))

# ---------------------------------------------------------------- fondos
BG = os.path.join(SRC, 'bg', 'Files')
layers = {n: uri(Image.open(os.path.join(BG, n + '.png')).convert('RGBA')) for n in
          ['Fuji', 'Mountain_Back', 'Mountain_Middle', 'Mountain_Front', 'BackgroundTrees', 'Shrine_Multiple', 'Shrine_Single', 'Trees', 'House']}
tb = Image.open(os.path.join(SRC, 'tiles', 'Background.png')).convert('RGBA')
bbs = [tb.crop((16, 0, 112, 176)), tb.crop((128, 0, 224, 176)), tb.crop((240, 0, 352, 176))]
strip = Image.new('RGBA', (sum(b.width for b in bbs) * 2 + 24, 176)); x = 0
for k in range(2):
    for b in (bbs if k == 0 else bbs[::-1]):
        bx = b.getbbox(); c = b.crop(bx); strip.alpha_composite(c, (x, 176 - c.height)); x += c.width + 4
strip = strip.crop((0, 0, x, 176))
layers['Town'] = uri(strip)

# ---------------------------------------------------------------- retratos
fs = Image.open(os.path.join(SRC, 'chars', '64X64 Face', 'sheet.png')).convert('RGBA')
faces = {'Aoi': uri(fs.crop((64, 0, 128, 64))), 'Haru': uri(fs.crop((128, 192, 192, 256)))}

js = 'window.WD_ASSETS=' + json.dumps(dict(sprites=uri(atlas), meta=meta, layers=layers, faces=faces)) + ';'
open(os.path.join(OUT, 'assets.js'), 'w').write(js)
print('ok', len(js) // 1024, 'KB')
