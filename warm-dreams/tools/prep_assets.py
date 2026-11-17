"""Convierte las imágenes de SpriteCook (assets.local/fase*/) al tamaño del juego
y las agrega a assets.local/assets.js (window.WD_ASSETS). No sube nada al repo.

Escala del juego: 1 unidad = 2 px lógicos; el render final es 1.5x (3 px por unidad).
Las imágenes se guardan a 3 px por unidad para verse nítidas.

Uso: python3 -I tools/prep_assets.py
"""
import base64, io, json, os, sys
from PIL import Image
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
    lit = light_layer(Image.open(os.path.join(ROOT, 'fase0/edificio_luces.png')), box, im.size)
    la = np.asarray(lit).copy(); la[..., 3] = np.where(np.asarray(im)[..., 3] > 0, la[..., 3], 0)
    # solo tonos cálidos (quita la ropa y el aire acondicionado)
    warm = (la[..., 0].astype(int) > la[..., 2].astype(int) + 25)
    la[..., 3] = np.where(warm, la[..., 3], 0); lit = Image.fromarray(la, 'RGBA')
    A['buildings']['tiendaCafe'] = {'src': b64(im), 'glow': b64(lit), 'w': round(im.width / K * 2), 'h': hu * 2,
                                    'lights': blobs(lit, 2 / K)}

    open(path, 'w').write('window.WD_ASSETS=' + json.dumps(A) + ';')
    print('ok', {k: (list(v.keys()) if isinstance(v, dict) else len(v)) for k, v in A.items()},
          round(os.path.getsize(path) / 1024), 'KB')


if __name__ == '__main__':
    sys.exit(main())
