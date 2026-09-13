#!/usr/bin/env python3
"""Banner propio para /publicaciones/: la produccion del laboratorio por ano.

El masthead le aplica encima un overlay negro al 50% y una animacion de zoom,
asi que el centro se deja tranquilo y el peso visual va abajo.
"""

import math
import pathlib

from PIL import Image, ImageDraw, ImageFilter

W, H = 2400, 1000
OUT = pathlib.Path(__file__).resolve().parents[2] / "assets" / "img"

# publicaciones por ano (mismo dataset que la pagina)
SERIE = [
    (2017, 2),
    (2018, 1),
    (2019, 1),
    (2020, 4),
    (2021, 3),
    (2022, 3),
    (2023, 4),
    (2024, 4),
    (2025, 3),
    (2026, 8),
]

TOP = (15, 38, 72)  # navy profundo
BOTTOM = (28, 84, 150)  # azul UNLu mas claro
ACCENT = (94, 190, 255)


def gradiente():
    base = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(base)
    for y in range(H):
        t = y / H
        # curva suave para que el degrade no sea lineal plano
        t = t**0.85
        d.line(
            [(0, y), (W, y)],
            fill=tuple(int(TOP[i] + (BOTTOM[i] - TOP[i]) * t) for i in range(3)),
        )
    # halo diagonal
    halo = Image.new("L", (W, H), 0)
    hd = ImageDraw.Draw(halo)
    hd.ellipse([W * 0.45, -H * 0.55, W * 1.25, H * 0.85], fill=110)
    halo = halo.filter(ImageFilter.GaussianBlur(260))
    base = Image.composite(Image.new("RGB", (W, H), (52, 118, 190)), base, halo)
    return base


def grilla(img):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for i in range(1, 9):
        y = int(H * i / 9)
        d.line([(0, y), (W, y)], fill=(255, 255, 255, 20), width=1)
    for i in range(1, 24):
        x = int(W * i / 24)
        d.line([(x, 0), (x, H)], fill=(255, 255, 255, 14), width=1)
    return Image.alpha_composite(img.convert("RGBA"), layer)


def constelacion(img):
    """Nodos tenues conectados, densidad creciente hacia la derecha."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    rnd = 12345
    for i in range(150):
        rnd = (1103515245 * rnd + 12345) % (2**31)
        x = (rnd / 2**31) ** 0.65 * W
        rnd = (1103515245 * rnd + 12345) % (2**31)
        y = (rnd / 2**31) * H * 0.78
        pts.append((x, y))
    for i, (x1, y1) in enumerate(pts):
        for x2, y2 in pts[i + 1 :]:
            dist = math.hypot(x2 - x1, y2 - y1)
            if dist < 155:
                a = int(58 * (1 - dist / 155))
                d.line([(x1, y1), (x2, y2)], fill=(*ACCENT, a), width=1)
    for x, y in pts:
        d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(*ACCENT, 140))
    return Image.alpha_composite(img, layer)


def barras(img):
    """Produccion por ano, apoyada sobre el borde inferior."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    n = len(SERIE)
    margen = W * 0.06
    ancho_total = W - 2 * margen
    paso = ancho_total / n
    bw = paso * 0.34
    tope = max(c for _, c in SERIE)
    base_y = H - 70
    for i, (anio, cant) in enumerate(SERIE):
        cx = margen + paso * (i + 0.5)
        alto = (cant / tope) * (H * 0.30)
        x0, x1 = cx - bw / 2, cx + bw / 2
        # barra con degrade vertical propio
        for k in range(int(alto)):
            t = k / max(alto, 1)
            a = int(70 + 130 * t)
            y = base_y - k
            d.line([(x0, y), (x1, y)], fill=(*ACCENT, a))
        # remate superior
        d.line(
            [(x0, base_y - alto), (x1, base_y - alto)],
            fill=(205, 240, 255, 255),
            width=3,
        )
    # linea de base
    d.line(
        [(margen * 0.6, base_y + 10), (W - margen * 0.6, base_y + 10)],
        fill=(255, 255, 255, 40),
        width=2,
    )
    return Image.alpha_composite(img, layer)


img = gradiente()
img = grilla(img)
img = constelacion(img)
img = barras(img)
img = img.convert("RGB")
# viñeteado suave para que el texto centrado respire
vig = Image.new("L", (W, H), 0)
ImageDraw.Draw(vig).ellipse([-W * 0.15, -H * 0.35, W * 1.15, H * 1.35], fill=255)
vig = vig.filter(ImageFilter.GaussianBlur(200))
img = Image.composite(img, Image.new("RGB", (W, H), (9, 24, 48)), vig)

OUT.mkdir(parents=True, exist_ok=True)
img.save(OUT / "banner-publicaciones.jpg", quality=88, optimize=True)
img.save(OUT / "banner-publicaciones.webp", quality=82, method=6)
print("jpg :", (OUT / "banner-publicaciones.jpg").stat().st_size // 1024, "KB")
print("webp:", (OUT / "banner-publicaciones.webp").stat().st_size // 1024, "KB")

# preview con el overlay negro al 50% que aplica el CSS, para juzgarlo como se ve de verdad
prev = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), 0.5)
prev.resize((1000, 417)).save(
    pathlib.Path(__file__).with_name("banner-preview.png")
)
print("preview con overlay generado")
