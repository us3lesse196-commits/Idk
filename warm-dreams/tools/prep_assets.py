"""Convierte las imágenes de SpriteCook (assets.local/fase*/) al tamaño del juego
y las agrega a assets.local/assets.js (window.WD_ASSETS). No sube nada al repo.

Escala del juego: 1 unidad = 2 px lógicos; el render final es 1.5x (3 px por unidad).
Las imágenes se guardan a 3 px por unidad para verse nítidas.

Uso: python3 -I tools/prep_assets.py
"""
import base64, io, json, os, sys
from PIL import Image, ImageFilter
import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets.local')
K = 3  # px reales por unidad


def load(path):
    return Image.open(os.path.join(ROOT, path)).convert('RGBA')


def bbox(im, thr=40):
    a = np.asarray(im)[..., 3]
    ys, xs = np.where(a > thr)
    return (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)


def harden(im, thr=120):
    a = np.asarray(im).copy()
    a[..., 3] = np.where(a[..., 3] > thr, 255, 0)
    return Image.fromarray(a, 'RGBA')


def fit_h(im, h):
    w = max(1, round(im.width * h / im.height))
    return im.resize((w, h), Image.BOX)


def b64(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def register(src_rgba, light_rgb):
    """Alinea la imagen de luces con el edificio (la IA a veces la desplaza o la escala).
    Busca escala y desplazamiento que mejor ponen la luz sobre los vidrios oscuros."""
    S = 320
    W, H = src_rgba.size; k = S / max(W, H)
    sw, sh = round(W * k), round(H * k)
    a = np.asarray(src_rgba.resize((sw, sh), Image.BOX)).astype(float)
    lum = (a[..., 0] * 3 + a[..., 1] * 6 + a[..., 2]) / 10
    glass = ((a[..., 3] > 100) & (lum < 110) & (a[..., 2] >= a[..., 0] - 6)).astype(float)
    lit_full = light_rgb.convert('RGB').resize((W, H), Image.BOX)
    best = (-1, 1.0, 0, 0)
    for sc in np.linspace(0.9, 1.1, 21):
        lw, lh = round(sw * sc), round(sh * sc)
        L = np.asarray(lit_full.resize((lw, lh), Image.BOX)).astype(float).max(axis=2) > 80
        for dx in range(-24, 25, 2):
            for dy in range(-24, 25, 2):
                ox = (sw - lw) // 2 + dx; oy = (sh - lh) // 2 + dy
                x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(sw, ox + lw), min(sh, oy + lh)
                if x1 <= x0 or y1 <= y0: continue
                lm = L[y0 - oy:y1 - oy, x0 - ox:x1 - ox]
                gm = glass[y0:y1, x0:x1]
                hit = (lm * gm).sum() - 0.6 * (lm * (1 - gm)).sum()
                if hit > best[0]: best = (hit, sc, dx, dy)
    L0 = np.asarray(lit_full.resize((sw, sh), Image.BOX)).astype(float).max(axis=2) > 80
    ident = (L0 * glass).sum() - 0.6 * (L0 * (1 - glass)).sum()
    _, sc, dx, dy = best
    if best[0] < ident * 1.04 + 4 or abs(dy) > 14:
        sc, dx, dy = 1.0, 0, 0
    lw, lh = round(W * sc), round(H * sc)
    big = lit_full.resize((lw, lh), Image.BOX)
    out = Image.new('RGB', (W, H), (0, 0, 0))
    ox = (W - lw) // 2 + round(dx / k); oy = (H - lh) // 2 + round(dy / k)
    out.paste(big, (ox, oy))
    print('  alineado: escala %.3f  dx %d  dy %d' % (sc, round(dx / k), round(dy / k)))
    return out


def align_night(day_rgba, night_rgba):
    """Alinea la versión de noche (luces encendidas) con la de día comparando bordes."""
    W, H = day_rgba.size; S = 360; k = S / max(W, H); sw, sh = round(W * k), round(H * k)
    def edges(im, w, h):
        g = np.asarray(im.convert('L').resize((w, h), Image.BOX)).astype(float)
        e = np.abs(np.diff(g, axis=0, prepend=g[:1])) + np.abs(np.diff(g, axis=1, prepend=g[:, :1]))
        return e / (e.mean() + 1e-6)
    D = edges(day_rgba, sw, sh)
    night_full = night_rgba.convert('RGBA').resize((W, H), Image.BOX)
    best = (-1e9, 1.0, 0, 0)
    for sc in np.linspace(0.9, 1.1, 21):
        lw, lh = round(sw * sc), round(sh * sc); N = edges(night_full, lw, lh)
        for dx in range(-16, 17):
            for dy in range(-16, 17):
                ox = (sw - lw) // 2 + dx; oy = (sh - lh) // 2 + dy
                x0, y0 = max(0, ox), max(0, oy); x1, y1 = min(sw, ox + lw), min(sh, oy + lh)
                if x1 - x0 < sw * .8 or y1 - y0 < sh * .8: continue
                sc_ = (N[y0 - oy:y1 - oy, x0 - ox:x1 - ox] * D[y0:y1, x0:x1]).mean()
                if sc_ > best[0]: best = (sc_, sc, dx, dy)
    _, sc, dx, dy = best
    lw, lh = round(W * sc), round(H * sc)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.paste(night_full.resize((lw, lh), Image.BOX), ((W - lw) // 2 + round(dx / k), (H - lh) // 2 + round(dy / k)))
    print('  noche alineada: escala %.3f dx %d dy %d' % (sc, round(dx / k), round(dy / k)))
    return out


def lit_from_night(day_crop, night_crop):
    """Capa emisiva = píxeles de la versión encendida donde brilla (interiores, faroles), con borde suave."""
    n = np.asarray(night_crop).astype(float); d = np.asarray(day_crop).astype(float)
    lum = (n[..., 0] * 3 + n[..., 1] * 6 + n[..., 2]) / 10
    warmth = n[..., 0] - n[..., 2]
    m = np.clip((lum - 95) / 70, 0, 1) * np.clip((warmth + 40) / 60, 0.35, 1)
    m = np.asarray(Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))).astype(float) / 255
    m = m * (d[..., 3] > 0)
    out = np.dstack([n[..., :3], m * 245]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def light_layer(img_rgb, box, size):
    """Imagen de luces (fondo negro) -> RGBA con alfa según brillo."""
    a = np.asarray(img_rgb.convert('RGB').crop(box).resize(size, Image.BOX)).astype(float)
    lum = a.max(axis=2)
    alpha = np.clip((lum - 55) * 2.2, 0, 255)
    out = np.dstack([a, alpha]).astype(np.uint8)
    return Image.fromarray(out, 'RGBA')


def blobs(light_rgba, scale):
    """Manchas de luz -> [x, y, tamaño] en px lógicos (2 px por unidad)."""
    a = np.asarray(light_rgba)[..., 3] > 140
    h, w = a.shape
    seen = np.zeros_like(a)
    out = []
    for y in range(h):
        for x in range(w):
            if a[y, x] and not seen[y, x]:
                st = [(y, x)]; seen[y, x] = 1; pts = []
                while st:
                    cy, cx = st.pop(); pts.append((cy, cx))
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < h and 0 <= nx < w and a[ny, nx] and not seen[ny, nx]:
                            seen[ny, nx] = 1; st.append((ny, nx))
                if len(pts) >= 6:
                    ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                    out.append([round(sum(xs) / len(xs) * scale), round(sum(ys) / len(ys) * scale), len(pts)])
    return out


def proc_glow(im, mode, seed=0):
    """Capa de luces calculada: ventanas (vidrio oscuro) encendidas al azar o tonos cálidos."""
    a = np.asarray(im).astype(int); r, g, bl, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
    lum = (r * 3 + g * 6 + bl) / 10; out = np.zeros(a.shape, np.uint8)
    rng = np.random.default_rng(seed)
    if mode in ('school', 'tower'):
        glass = (al > 0) & (bl >= r - 4) & (lum < 120) & (lum > 18)
        h, w = glass.shape; lab = np.zeros((h, w), int); n = 0
        for y in range(h):
            for x in range(w):
                if glass[y, x] and not lab[y, x]:
                    n += 1; st = [(y, x)]; lab[y, x] = n; pts = []
                    while st:
                        cy, cx = st.pop(); pts.append((cy, cx))
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < h and 0 <= nx < w and glass[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; st.append((ny, nx))
                    if len(pts) > 40:
                        ys = [p_[0] for p_ in pts]; xs = [p_[1] for p_ in pts]
                        y0, y1, x0, x1 = min(ys), max(ys), min(xs), max(xs)
                        fill = len(pts) / max(1, (y1 - y0 + 1) * (x1 - x0 + 1))
                        if fill > 0.45 and (x1 - x0) > 3 and (y1 - y0) > 3 and rng.random() < (0.5 if mode == 'school' else 0.8):
                            warm = rng.random() < 0.85
                            col = (255, 226, 160) if warm else (190, 215, 255)
                            for (py, px) in pts:
                                out[py, px] = (*col, 228)
        if mode == 'tower':
            top = h // 4
            face = (al[:top] > 0) & (lum[:top] > 200)
            out[:top][face] = (255, 246, 220, 220)
    else:
        warm = (al > 0) & (r > 150) & (r - bl > 60) & (r >= g)
        cream = (al > 0) & (lum > 205)
        m = warm | cream
        out[m, :3] = a[m, :3]; out[m, 3] = 235
    return Image.fromarray(out, 'RGBA')


CROPR = {'tramoS3': 0.915}  # recorte por la derecha (quita la pared vecina cortada)


def cbox(name, src):
    b = bbox(src)
    if name in CROPR: b = (b[0], b[1], b[0] + round((b[2] - b[0]) * CROPR[name]), b[3])
    return b


def split_sheet(path, S=512, thr=60, minpx=300):
    """Separa una hoja de objetos en imágenes sueltas (máscara por componente)."""
    im = Image.open(path).convert('RGBA'); k = im.width / S
    a = np.asarray(im.split()[3].resize((S, S), Image.BOX)) > thr
    lab = np.zeros(a.shape, int); n = 0; comps = []
    for y in range(S):
        for x in range(S):
            if a[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n; xs = []; ys = []
                while st:
                    cy, cx = st.pop(); xs.append(cx); ys.append(cy)
                    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                        ny, nx = cy + dy, cx + dx
                        if 0 <= ny < S and 0 <= nx < S and a[ny, nx] and not lab[ny, nx]:
                            lab[ny, nx] = n; st.append((ny, nx))
                comps.append({'ids': [n], 'b': [min(xs), min(ys), max(xs) + 1, max(ys) + 1], 'n': len(xs)})
    comps = [c for c in comps if c['n'] > minpx // 4]; comps.sort(key=lambda c: -c['n']); keep = []
    for c in comps:
        b = c['b']; host = None
        for h in keep:
            hb = h['b']; ox = min(b[2], hb[2]) - max(b[0], hb[0]); oy = min(b[3], hb[3]) - max(b[1], hb[1])
            if ox > 0.6 * (b[2] - b[0]) and oy > -4: host = h; break
        if host:
            host['ids'] += c['ids']; hb = host['b']; host['b'] = [min(hb[0], b[0]), min(hb[1], b[1]), max(hb[2], b[2]), max(hb[3], b[3])]
        elif c['n'] > minpx: keep.append(c)
    keep.sort(key=lambda c: (round(c['b'][3] / 60), c['b'][0]))
    out = []
    for c in keep:
        m = np.isin(lab, c['ids']).astype(np.uint8) * 255
        mk_ = Image.fromarray(m).filter(ImageFilter.MaxFilter(3)).resize(im.size, Image.NEAREST)
        part = im.copy(); part.putalpha(Image.fromarray(np.minimum(np.asarray(part.split()[3]), np.asarray(mk_))))
        bb = [int(v * k) for v in c['b']]; part = part.crop((max(0, bb[0] - 4), max(0, bb[1] - 4), min(im.width, bb[2] + 4), min(im.height, bb[3] + 4)))
        out.append(part.crop(part.getbbox()))
    return out


def main():
    path = os.path.join(ROOT, 'assets.js')
    s = open(path).read() if os.path.exists(path) else 'window.WD_ASSETS={}'
    A = json.loads(s[s.index('{'):s.rindex('}') + 1])

    # ---- árboles (alto en unidades del juego)
    trees = {}
    for key, f, h_units in [('a', 'fase0/cerezo_a.png', 84), ('b', 'fase0/cerezo_b.png', 84),
                            ('lloron', 'fase1/cerezo_lloron.png', 80), ('joven', 'fase1/cerezo_joven.png', 74),
                            ('sagrado', 'fase0/sagrado_b.png', 112), ('bambu', 'props/bambu.png', 58), ('arce', 'props/arce.png', 46)]:
        im = load(f); im = im.crop(bbox(im)); im = harden(fit_h(im, h_units * K))
        trees[key] = {'src': b64(im), 'w': im.width / K, 'h': h_units}
    A['trees'] = trees

    # ---- capas de fondo (alto en px lógicos; se dibujan a 1.5x)
    far = {}
    for key, f, lh in [('montanas', 'fase0/montanas.png', 150), ('cordillera', 'fase1/cordillera.png', 70),
                       ('colinas', 'fase1/colinas.png', 92), ('ciudad', 'fase1/ciudad.png', 74)]:
        im = load(f); box = bbox(im, 30); im = im.crop(box); im = fit_h(im, round(lh * 1.5))
        far[key] = {'src': b64(im), 'lw': im.width / 1.5, 'lh': lh}
        if key == 'ciudad':
            lit = light_layer(Image.open(os.path.join(ROOT, 'fase1/ciudad_luces.png')), box, im.size)
            far['ciudadLuz'] = {'src': b64(lit), 'lw': im.width / 1.5, 'lh': lh}
    src = load('fase1/barrio.png'); box = bbox(src, 30); im = fit_h(src.crop(box), round(120 * 1.5))
    far['barrio'] = {'src': b64(im), 'lw': im.width / 1.5, 'lh': 120}
    nim = Image.open(os.path.join(ROOT, 'fase1/barrio_noche.png')).convert('RGBA').resize(src.size, Image.BOX).crop(box).resize(im.size, Image.BOX)
    far['barrioLuz'] = {'src': b64(lit_from_night(im, nim)), 'lw': im.width / 1.5, 'lh': 120}
    A['far'] = far

    # ---- nubes: separar las 5 de la hoja
    sheet = load('cielo/nubes2.png') if os.path.exists(os.path.join(ROOT, 'cielo/nubes2.png')) else load('fase1/nubes.png').resize((420, 420), Image.BOX)
    a = np.asarray(sheet)[..., 3] > 40
    lab = np.zeros(a.shape, int); n = 0; comps = []
    for y in range(a.shape[0]):
        for x in range(a.shape[1]):
            if a[y, x] and not lab[y, x]:
                n += 1; st = [(y, x)]; lab[y, x] = n; xs = []; ys = []
                while st:
                    cy, cx = st.pop(); xs.append(cx); ys.append(cy)
                    for dy in (-2, -1, 0, 1, 2):
                        for dx in (-2, -1, 0, 1, 2):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < a.shape[0] and 0 <= nx < a.shape[1] and a[ny, nx] and not lab[ny, nx]:
                                lab[ny, nx] = n; st.append((ny, nx))
                if len(xs) > 300:
                    comps.append((min(xs), min(ys), max(xs) + 1, max(ys) + 1))
    A['clouds'] = [{'src': b64(sheet.crop(c)), 'lw': (c[2] - c[0]) / 1.5, 'lh': (c[3] - c[1]) / 1.5} for c in comps]

    # ---- edificio tienda-cafetería con su imagen de luces
    im = load('fase0/edificio.png'); box = bbox(im); im = im.crop(box)
    hu = 72; im = harden(fit_h(im, hu * K), 100)
    lit = light_layer(register(load('fase0/edificio.png'), Image.open(os.path.join(ROOT, 'fase0/edificio_luces.png'))), box, im.size)
    la = np.asarray(lit).copy(); la[..., 3] = np.where(np.asarray(im)[..., 3] > 0, la[..., 3], 0)
    # solo tonos cálidos (quita la ropa y el aire acondicionado)
    warm = (la[..., 0].astype(int) > la[..., 2].astype(int) + 25)
    la[..., 3] = np.where(warm, la[..., 3], 0); lit = Image.fromarray(la, 'RGBA')
    A['buildings']['tiendaCafe'] = {'src': b64(im), 'glow': b64(lit), 'w': round(im.width / K * 2), 'h': hu * 2,
                                    'lights': blobs(lit, 2 / K)}

    # ---- fase 2: calle
    for name, f, lf, hu in [('dagashiya', 'fase2/dagashiya_sq.png', 'fase2/dagashiya_luces.png', 70),
                            ('casaN', 'fase2/casaN_sq.png', 'fase2/casaN_luces.png', 76),
                            ('casaMori', 'fase2/casaMori.png', 'fase2/casaMori_luces.png', 64),
                            ('casaC', 'fase2/casaC.png', 'fase2/casaC_luces.png', 38),
                            ('deptos', 'fase2/deptos.png', 'fase2/deptos_luces.png', 104),
                            ('parada', 'fase2/parada.png', None, 34)]:
        src = load(f); box = bbox(src); im = harden(fit_h(src.crop(box), hu * K), 100)
        e = {'src': b64(im), 'w': round(im.width / K * 2), 'h': hu * 2, 'lights': []}
        if lf:
            L = register(src, Image.open(os.path.join(ROOT, lf)))
            lit = light_layer(L, box, im.size)
            la = np.asarray(lit).copy(); la[..., 3] = np.where(np.asarray(im)[..., 3] > 0, la[..., 3], 0)
            warm = (la[..., 0].astype(int) > la[..., 2].astype(int) + 25)
            la[..., 3] = np.where(warm, la[..., 3], 0); lit = Image.fromarray(la, 'RGBA')
            e['glow'] = b64(lit); e['lights'] = blobs(lit, 2 / K)
        A['buildings'][name] = e

    # ---- fase 3: prepa y entrada del callejón (luces calculadas por código)
    for name, f, nf, hu in [('alaA', 'fase3/alaA_up.png', 'fase3/alaA_noche.png', 75), ('alaAm', 'fase3/alaA_up.png', 'fase3/alaA_noche.png', 75),
                            ('centro', 'fase3/centro_up.png', 'fase3/centro_noche.png', 75)]:
        src = load(f); box = bbox(src); im = harden(fit_h(src.crop(box), hu * K), 100)
        night = align_night(src, Image.open(os.path.join(ROOT, nf)))
        lit = lit_from_night(im, fit_h(night.crop(box), hu * K).resize(im.size, Image.BOX))
        if name.endswith('m'): im = im.transpose(Image.FLIP_LEFT_RIGHT); lit = lit.transpose(Image.FLIP_LEFT_RIGHT)
        A['buildings'][name] = {'src': b64(im), 'glow': b64(lit), 'w': round(im.width / K * 2), 'h': hu * 2, 'lights': blobs(lit, 2 / K)}
    for k in ('alaB', 'torre', 'shop', 'house', 'cafe'): A['buildings'].pop(k, None)
    for name, f, hu, mode in [('porton', 'fase3/porton.png', 47, None),
                              ('callejonEntrada', 'fase3/callejonEntrada.png', 60, 'warm')]:
        src = load(f); im = harden(fit_h(src.crop(bbox(src)), hu * K), 100)
        if name.endswith('m'): im = im.transpose(Image.FLIP_LEFT_RIGHT)
        e = {'src': b64(im), 'w': round(im.width / K * 2), 'h': hu * 2, 'lights': []}
        if mode:
            lit = proc_glow(im, mode, seed=len(name))
            e['glow'] = b64(lit); e['lights'] = blobs(lit, 2 / K)
        A['buildings'][name] = e

    # ---- tramos pintados de una vez (edificios conectados)
    for name, f, hu in [('tramoCallejon', 'tramos/callejon_a.png', 128), ('tramoS1', 'tramos/s1.png', 80), ('tramoS2', 'tramos/s2.png', 75), ('tramoS3', 'tramos/s3.png', 72)]:
        src = load(f); im = harden(fit_h(src.crop(cbox(name, src)), hu * K), 100)
        A['buildings'][name] = {'src': b64(im), 'w': round(im.width / K * 2), 'h': hu * 2, 'lights': []}

    # ---- versiones de noche con luces encendidas (interiores reales)
    NIGHT = {'tramoCallejon': ('tramos/callejon_a.png', 128), 'tramoS1': ('tramos/s1.png', 80), 'tramoS2': ('tramos/s2.png', 75), 'tramoS3': ('tramos/s3.png', 72), 'tiendaCafe': ('fase0/edificio.png', 72), 'dagashiya': ('fase2/dagashiya_sq.png', 70), 'casaN': ('fase2/casaN_sq.png', 76),
             'casaMori': ('fase2/casaMori.png', 64), 'casaC': ('fase2/casaC.png', 38), 'deptos': ('fase2/deptos.png', 104),
             'callejonEntrada': ('fase3/callejonEntrada.png', 60)}
    for name, (f, hu) in NIGHT.items():
        nf = os.path.join(ROOT, 'noche', name + '.png')
        if not os.path.exists(nf) or name not in A['buildings']: continue
        src = load(f); srcC = src.crop(cbox(name, src)); im = harden(fit_h(srcC, hu * K), 100)
        nim = Image.open(nf).convert('RGBA'); nb = bbox(nim, 30)
        if name in CROPR: nb = (nb[0], nb[1], nb[0] + round((nb[2] - nb[0]) * CROPR[name]), nb[3])
        nim = nim.crop(nb)
        night = align_night(srcC, nim)
        lit = lit_from_night(im, night.resize(im.size, Image.BOX))
        A['buildings'][name].update({'glow': b64(lit), 'lights': blobs(lit, 2 / K)})

    # ---- cruce del tren (vista de lado) y tren
    X = {}
    src = load('tren/cruce_ok.png'); im = fit_h(src.crop(bbox(src, 30)), 65 * K)
    X['cruce'] = {'src': b64(im), 'w': im.width / K, 'h': 65}
    for name in ('vagon', 'cabina'):
        src = load('tren/%s_ok.png' % name); box = bbox(src, 30); im = harden(fit_h(src.crop(box), 34 * K), 100)
        nim = Image.open(os.path.join(ROOT, 'tren/%s_noche_ok.png' % name)).convert('RGBA').crop(box).resize(im.size, Image.BOX)
        X[name] = {'src': b64(im), 'glow': b64(lit_from_night(im, nim)), 'w': im.width / K, 'h': 34}
    A['xing'] = X
    # ---- suelos (texturas repetibles)
    G = {}
    im = load('suelo/calle.png').convert('RGB'); hh = 40 * K; im = im.resize((round(im.width * hh / im.height), hh), Image.BOX).crop((0, 0, round(im.width * hh / im.height), 30 * K))
    G['calle'] = {'src': b64(im), 'w': im.width / K, 'h': 30}
    im = load('suelo/campo.png').convert('RGB'); im = im.crop((0, 150, im.width, im.height)); hh = 34 * K
    im = im.resize((round(im.width * hh / im.height), hh), Image.BOX).crop((0, 0, round(im.width * hh / im.height), 30 * K))
    G['campo'] = {'src': b64(im), 'w': im.width / K, 'h': 30}
    A['ground'] = G
    # ---- decoración (hojas de objetos)
    D = {}
    names = {'deco/plantas.png': [('boj', 9), ('seto', 8), ('bambuMaceta', 22), ('hortensia', 9), ('bonsai', 12), ('hierba', 6), ('pampas', 18), ('azalea', 8)],
             'deco/calle.png': [('farol', 44), ('banca', 9), ('bicis', 11), ('botes', 11), ('tablon', 22), ('jardinera', 8), ('senal', 22), ('valla', 7)],
             'deco/campo.png': [('espantapajaros', 20), ('jizo', 9), ('cerca', 9), ('caseta', 24), ('juncos', 18), ('arroz', 13), ('linterna', 13)]}
    for f, lst in names.items():
        parts = split_sheet(os.path.join(ROOT, f))
        assert len(parts) == len(lst), (f, len(parts))
        for (nm, hu), part in zip(lst, parts):
            im = harden(fit_h(part, hu * K), 100); D[nm] = {'src': b64(im), 'w': im.width / K, 'h': hu}
    A['deco'] = D
    # ---- lago con puente y túnel
    src = load('lago/lago_b.png'); im = fit_h(src.crop(bbox(src)), 95 * K)
    _a = np.asarray(im).copy(); _w, _h = im.width, im.height; _a[:int(_h * .5), int(_w * .9):, 3] = 0; im = Image.fromarray(_a, 'RGBA')
    a_ = np.asarray(im).astype(int); red = (a_[..., 0] > 140) & (a_[..., 1] < 95) & (a_[..., 2] < 90) & (a_[..., 3] > 200)
    W_ = im.width; top = np.full(W_, -1)
    for x in range(W_):
        ys = np.where(red[:, x])[0]
        if len(ys): top[x] = ys.min()
    cols = np.where(top >= 0)[0]; x0, x1 = cols.min(), cols.max()
    t = top.astype(float); 
    for x in range(W_):
        if t[x] < 0: t[x] = np.nan
    prof = []
    for u in range(int(W_ / K)):
        seg = t[u * K:(u + 1) * K + 12]; seg = seg[~np.isnan(seg)]
        prof.append(round(float(np.median(seg)) / K, 1) if len(seg) else None)
    # extremos: fila donde termina el puente (cubierta) = parte baja de lo rojo en las orillas
    redrows = np.where(red[:, x0:x0 + 6 * K].any(axis=1))[0]
    deckEnd = round(float(redrows.max()) / K, 1)
    A['lago'] = {'src': b64(im), 'w': W_ / K, 'h': 95, 'rail': prof, 'x0': round(x0 / K, 1), 'x1': round(x1 / K, 1), 'deckEnd': deckEnd}
    # barandilla delantera: franja desde arriba del pasamanos hasta el tablero (DECK unidades), sin vegetación
    DECK = 13; fr = np.zeros_like(np.asarray(im)); src_a = np.asarray(im)
    g_ = (a_[..., 1] > a_[..., 0] + 8) & (a_[..., 1] > a_[..., 2])
    for x in range(x0, x1 + 1):
        if top[x] < 0: continue
        y0 = max(0, top[x] - 5 * K); y1 = min(_h, top[x] + DECK * K)
        col = (src_a[y0:y1, x, 3] > 100) & ~g_[y0:y1, x]
        fr[y0:y1, x][col] = src_a[y0:y1, x][col]
    A['lago']['front'] = b64(Image.fromarray(fr, 'RGBA')); A['lago']['deck'] = DECK
    A.pop('tunel', None)
    # ---- santuario y colina
    A['buildings'].pop('shrine', None)
    S_ = {}
    src = load('santuario/haiden.png'); box = bbox(src, 30); im = harden(fit_h(src.crop(box), 58 * K), 100)
    nim = load('santuario/haiden_noche.png'); nim = align_night(src.crop(box), nim.crop(bbox(nim, 30))).resize(im.size, Image.BOX)
    S_['haiden'] = {'src': b64(im), 'glow': b64(lit_from_night(im, nim)), 'w': im.width / K, 'h': 58}
    im = load('santuario/muro.png').convert('RGB'); hh = 54 * K; im = im.resize((round(im.width * hh / im.height), hh), Image.BOX)
    S_['muro'] = {'src': b64(im), 'w': im.width / K, 'h': 54}
    for (nm, hu), part in zip([('torii', 40), ('kitsuneR', 15), ('kitsuneL', 15), ('temizuya', 19), ('ema', 18), ('omikuji', 17), ('barandal', 9)], split_sheet(os.path.join(ROOT, 'santuario/objetos.png'))):
        im = harden(fit_h(part, hu * K), 100); A['deco'][nm] = {'src': b64(im), 'w': im.width / K, 'h': hu}
    for (nm, hu), part in zip([('cedro', 104), ('pino', 70), ('arceRojo', 46)], split_sheet(os.path.join(ROOT, 'santuario/arboles.png'))):
        im = harden(fit_h(part, hu * K), 100); A['trees'][nm] = {'src': b64(im), 'w': im.width / K, 'h': hu}
    src = load('santuario/toriiL_b.png'); im = harden(fit_h(src.crop(bbox(src, 30)), 48 * K), 100)
    a_ = np.asarray(im).copy(); h_, w_ = a_.shape[:2]; fr = a_.copy()
    yy, xx = np.mgrid[0:h_, 0:w_]; front = (xx < w_ * .58) | (yy < h_ * .16)
    fr[..., 3] = np.where(front, fr[..., 3], 0)
    S_['toriiP'] = {'src': b64(im), 'front': b64(Image.fromarray(fr, 'RGBA')), 'w': w_ / K, 'h': 48}
    im = load('santuario/bosque.png').convert('RGB'); hh = 140 * K; im = im.resize((round(im.width * hh / im.height), hh), Image.BOX)
    S_['bosque'] = {'src': b64(im), 'w': im.width / K, 'h': 140}
    A['santuario'] = S_
    AL = []
    for f, nf in [('callejon/a1.png', 'callejon/a1n.png'), ('callejon/a2.png', 'callejon/a2n.png')]:
        src = load(f); box = bbox(src, 30); im = harden(fit_h(src.crop(box), 128 * K), 100)
        nim = load(nf).crop(box).resize(im.size, Image.BOX)
        AL.append({'src': b64(im), 'glow': b64(lit_from_night(im, nim)), 'w': im.width / K, 'h': 128})
    A['alley'] = AL
    U = {}
    ic = load('ui/iconos.png'); al = np.asarray(ic)[..., 3] > 60; cols = al.any(axis=0); segs = []; x = 0
    while x < len(cols):
        if cols[x]:
            x0 = x
            while x < len(cols) and cols[x]: x += 1
            if segs and x0 - segs[-1][1] < 60: segs[-1] = (segs[-1][0], x)
            else: segs.append((x0, x))
        x += 1
    segs = [sg for sg in segs if sg[1] - sg[0] > 15]
    assert len(segs) == 8, segs
    for nm, (x0, x1) in zip(['hora', 'pantalla', 'cuaderno', 'ajustes', 'izq', 'der', 'salto', 'abajo'], segs):
        rows = np.where(al[:, x0:x1].any(axis=1))[0]; part = ic.crop((x0, int(rows.min()), x1, int(rows.max()) + 1)); part.thumbnail((64, 64), Image.LANCZOS); U[nm] = b64(part)
    bt = load('ui/boton.png'); bt = bt.crop(bbox(bt, 30)); bt.thumbnail((160, 160), Image.LANCZOS); U['boton'] = b64(bt)
    A['ui'] = U
    src = load('casa/diag_b.png').convert('RGBA'); K2 = 3; s_ = 0.13 * K2
    im = src.resize((round(src.width * s_), round(src.height * s_)), Image.BOX)
    nim = load('casa/diag_noche.png').convert('RGBA').resize(im.size, Image.BOX)
    A['casaInt'] = {'src': b64(im), 'glow': b64(lit_from_night(im, nim)), 'w': im.width / K2, 'h': im.height / K2}
    src = load('lago/ladera.png'); im = fit_h(src.crop(bbox(src)), 95 * K)
    A['ladera'] = {'src': b64(im), 'w': im.width / K, 'h': 95}
    # ---- personajes de SpriteCook: hojas horizontales de cuadros cuadrados con los pies abajo
    def sheet(path, s_):
        sh = load(path); fh = sh.height; n = sh.width // fh; FW = round(fh * s_); out = Image.new('RGBA', (FW * n, FW))
        for j in range(n):
            fr = sh.crop((j * fh, 0, j * fh + fh, fh)).resize((FW, FW), Image.LANCZOS)
            out.paste(harden(fr, 110), (j * FW, 0))
        return {'src': b64(out), 'n': n, 'fw': FW, 'u': FW / K}

    def char(pre, anims, hu):
        """pre: prefijo de archivo; anims: [(nombre, fps)]; hu: alto en unidades (medido en el 1er cuadro del 1er anim)."""
        sh = load('chars/%s_%s.png' % (pre, anims[0][0])); fh = sh.height
        b = bbox(sh.crop((0, 0, fh, fh))); s_ = hu * K / (b[3] - b[1])
        d = {'ax': (b[0] + b[2]) / 2 * s_, 'by': (fh - b[3]) * s_ / K}
        for nm, fps in anims:
            if os.path.exists(os.path.join(ROOT, 'chars/%s_%s.png' % (pre, nm))): d[nm] = dict(sheet('chars/%s_%s.png' % (pre, nm), s_), fps=fps)
        d['fw'] = d[anims[0][0]]['fw']; d['u'] = d[anims[0][0]]['u']
        return d

    # Angel (protagonista; la clave 'haru' se conserva en el código)
    A['haru'] = char('angel', [('idle', 6), ('walk', 10), ('run', 14), ('jump', 10), ('back', 8)], 17)

    def hair_w(im):  # ancho del pelo rosa: sirve para igualar la escala de poses sueltas
        a = np.asarray(im.convert('RGBA')).astype(int); r, g, b_, al = a[..., 0], a[..., 1], a[..., 2], a[..., 3]
        xs = np.where(((al > 128) & (r > 185) & (b_ > 140) & (g < r - 25)).any(axis=0))[0]; return xs.max() - xs.min() + 1

    def pose(path, ref_hair_w, ref_scale):
        """pose fija: se escala para que el pelo mida lo mismo que en el reposo; cuadro cuadrado con pies abajo."""
        im = load(path); im = im.crop(bbox(im, 60)); s_ = ref_hair_w * ref_scale / hair_w(im)
        w, h = round(im.width * s_), round(im.height * s_); FW = max(w, h) + 2
        fr = Image.new('RGBA', (FW, FW)); fr.paste(harden(im.resize((w, h), Image.LANCZOS), 110), ((FW - w) // 2, FW - h))
        return {'src': b64(fr), 'n': 1, 'fw': FW, 'u': FW / K, 'fps': 1, 'ax': FW / 2, 'by': 0}

    ish = load('chars/angel_idle.png'); fh = ish.height; f0 = ish.crop((0, 0, fh, fh)); b0 = bbox(f0); sc0 = 17 * K / (b0[3] - b0[1])
    hw0 = hair_w(f0)
    for nm, f in [('sit', 'chars/angel_sitpose.png'), ('sleep', 'chars/angel_sleeppose.png'), ('slide', 'chars/slide_raw.png')]:
        if os.path.exists(os.path.join(ROOT, f)): A['haru'][nm] = pose(f, hw0, sc0)
    # NPC: estudiante, oficinista, abuelita, conserje (solo caminar) y Maju (reposo + caminar)
    NP = {}
    for nm, hu in [('student', 17), ('office', 18.5), ('granny', 15), ('janitor', 18)]:
        if os.path.exists(os.path.join(ROOT, 'chars/npc_%s_walk.png' % nm)): NP[nm] = char('npc_' + nm, [('walk', 8)], hu)
    if os.path.exists(os.path.join(ROOT, 'chars/maju_walk.png')): NP['aoi'] = char('maju', [('idle', 6), ('walk', 8)], 15.5)
    A['npc'] = NP
    # gatos (sprites fijos; respiran por código). alto en unidades
    CT = {}
    for nm, hu in [('naranja', 9), ('negro', 5.5), ('tricolor', 6.5)]:
        f = 'animals/gato_%s.png' % nm
        if os.path.exists(os.path.join(ROOT, f)):
            im = load(f); im = im.crop(bbox(im, 60)); im = harden(fit_h(im, round(hu * K)), 110)
            CT[nm] = {'src': b64(im), 'w': im.width / K, 'h': im.height / K}
    A['cats'] = CT
    if os.path.exists(os.path.join(ROOT, 'menu/logo.png')):
        im = load('menu/logo.png'); A['menu'] = {'logo': b64(im.crop(bbox(im, 20)))}
        for k, f in [('titulo', 'menu/titulo.png'), ('boton', 'menu/boton_menu.png')]:
            if os.path.exists(os.path.join(ROOT, f)): im = load(f); A['menu'][k] = b64(im.crop(bbox(im, 20)))
    # sol y luna (discos; el sol de día salió ovalado: se recorta y se fuerza a círculo)
    SK = {}
    for nm, f, d in [('luna', 'cielo/luna.png', 16), ('sol', 'cielo/sol.png', 20), ('solT', 'cielo/sol_tarde.png', 22)]:
        if os.path.exists(os.path.join(ROOT, f)):
            im = load(f); im = im.crop(bbox(im, 60)).resize((d * K, d * K), Image.NEAREST); SK[nm] = {'src': b64(im), 'd': d}
    A['sky'] = SK
    # retratos de diálogo (bustos con expresiones), 200 px de alto
    RT = {}
    for who, exprs in [('angel', ['hablar', 'pensar', 'sorprendido', 'feliz']), ('maju', ['hablar', 'timida', 'sorprendida', 'feliz']), ('zorro', ['tranquilo', 'curioso'])]:
        for ex in exprs:
            f = 'retratos/%s_%s.png' % (who, ex)
            if not os.path.exists(os.path.join(ROOT, f)): continue
            im = load(f); im = im.crop(bbox(im, 60))
            a_ = np.asarray(im)[..., 3] > 60; hh = int(im.height * .42); xs = np.where(a_[:hh].any(axis=0))[0]; head = xs.max() - xs.min() + 1
            if ex == exprs[0]: ref_s = 200 / im.height; ref_head = head * ref_s  # el primero (base) fija la escala
            s_ = ref_head / head; im = harden(im.resize((round(im.width * s_), round(im.height * s_)), Image.LANCZOS), 100)
            RT.setdefault(who, {})[ex] = b64(im)
    A['ret'] = RT
    if os.path.exists(os.path.join(ROOT, 'animals/koi.png')):
        im = load('animals/koi.png'); im = im.crop(bbox(im, 60)); w = round(9 * K); im = harden(im.resize((w, round(im.height * w / im.width)), Image.LANCZOS), 110)
        A['koi'] = {'src': b64(im), 'w': im.width / K, 'h': im.height / K}
    # zorro espíritu: reposo, caminar, desaparecer (alto ~15 unidades con la cola)
    if os.path.exists(os.path.join(ROOT, 'animals/zorro_idle.png')):
        A['fox'] = char('../animals/zorro', [('idle', 8), ('walk', 9), ('vanish', 10)], 15)
    print('  personajes', {k: round(v['u'], 1) for k, v in dict(NP, angel=A['haru']).items()})
    print('  lago w', W_ / K,'puente', A['lago']['x0'], A['lago']['x1'], 'deckEnd', deckEnd, 'ladera w', A['ladera']['w'])
    print('  cruce', X['cruce']['w'], 'vagon', X['vagon']['w'], 'cabina', X['cabina']['w'])

    open(path, 'w').write('window.WD_ASSETS=' + json.dumps(A) + ';')
    print('ok', {k: (list(v.keys()) if isinstance(v, dict) else len(v)) for k, v in A.items()},
          round(os.path.getsize(path) / 1024), 'KB')


if __name__ == '__main__':
    sys.exit(main())
