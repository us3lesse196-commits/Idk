"""Arma el HTML independiente: incrusta assets.local/assets.js (si existe) en index.html.
Uso: python3 -I tools/build.py 0.7  ->  dist/warm-dreams-0.7.html"""
import sys, os
here = os.path.join(os.path.dirname(__file__), '..')
ver = sys.argv[1]
src = open(os.path.join(here, 'index.html')).read()
ap = os.path.join(here, 'assets.local', 'assets.js')
if os.path.exists(ap):
    src = src.replace('<script id="wd-assets"></script>', '<script id="wd-assets">' + open(ap).read() + '</script>')
i = src.index('<canvas id="game"')
head = '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover,user-scalable=no">\n<meta name="theme-color" content="#0b0c20">\n'
os.makedirs(os.path.join(here, 'dist'), exist_ok=True)
out = os.path.join(here, 'dist', f'warm-dreams-{ver}.html')
open(out, 'w').write(head + src[:i] + '</head>\n<body>\n' + src[i:] + '\n</body>\n</html>\n')
print(out, os.path.getsize(out) // 1024, 'KB')
