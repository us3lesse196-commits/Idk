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


def main():
    path = os.path.join(ROOT, 'assets.js')
    s = open(path).read() if os.path.exists(path) else 'window.WD_ASSETS={}'
    A = json.loads(s[s.index('{'):s.rindex('}') + 1])

    # ---- árboles (alto en unidades del juego)
    trees = {}
    for key, f, h_units in [('a', 'fase0/cerezo_a.png', 84), ('b', 'fase0/cerezo_b.png', 84),
                            ('lloron', 'fase1/cerezo_lloron.png', 80), ('joven', 'fase1/cerezo_joven.png', 74),
                            ('sagrado', 'fase0/sagrado_b.png', 112)]:
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
    A['far'] = far

    # ---- nubes: separar las 5 de la hoja
    sheet = load('fase1/nubes.png'); sheet = sheet.resize((420, 420), Image.BOX)
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
    for name, f, hu in [('tramoCallejon', 'tramos/callejon_a.png', 128)]:
        src = load(f); im = harden(fit_h(src.crop(bbox(src)), hu * K), 100)
        A['buildings'][name] = {'src': b64(im), 'w': round(im.width / K * 2), 'h': hu * 2, 'lights': []}

    # ---- versiones de noche con luces encendidas (interiores reales)
    NIGHT = {'tramoCallejon': ('tramos/callejon_a.png', 128), 'tiendaCafe': ('fase0/edificio.png', 72), 'dagashiya': ('fase2/dagashiya_sq.png', 70), 'casaN': ('fase2/casaN_sq.png', 76),
             'casaMori': ('fase2/casaMori.png', 64), 'casaC': ('fase2/casaC.png', 38), 'deptos': ('fase2/deptos.png', 104),
             'callejonEntrada': ('fase3/callejonEntrada.png', 60)}
    for name, (f, hu) in NIGHT.items():
        nf = os.path.join(ROOT, 'noche', name + '.png')
        if not os.path.exists(nf) or name not in A['buildings']: continue
        src = load(f); srcC = src.crop(bbox(src)); im = harden(fit_h(srcC, hu * K), 100)
        nim = Image.open(nf).convert('RGBA'); nim = nim.crop(bbox(nim, 30))
        night = align_night(srcC, nim)
        lit = lit_from_night(im, night.resize(im.size, Image.BOX))
        A['buildings'][name].update({'glow': b64(lit), 'lights': blobs(lit, 2 / K)})

    open(path, 'w').write('window.WD_ASSETS=' + json.dumps(A) + ';')
    print('ok', {k: (list(v.keys()) if isinstance(v, dict) else len(v)) for k, v in A.items()},
          round(os.path.getsize(path) / 1024), 'KB')


if __name__ == '__main__':
    sys.exit(main())
