"""Compone cada recorte (PNG con transparencia) sobre fondo blanco con el mismo encuadre para todos.
Uso: python componer.py recorte/ final/"""
import json
import sys

from PIL import Image, ImageChops

ent, sal = sys.argv[1], sys.argv[2]
S = 480                     # lado del cuadrado de salida
CARA_ALTO = 0.32            # alto de la cara respecto del lado (referencia: la foto de Banchero)
CARA_MAX = 0.44             # tope cuando hay que agrandar para que el cuerpo llegue abajo
CARA_CY = 0.42              # centro de la cara, desde arriba
CY_MAX = 0.50               # se puede bajar la cara hasta acá si el cuerpo igual no llega
FUNDIDO_ABAJO = 0.32        # fundido del corte inferior cuando no alcanza el borde del lienzo
FUNDIDO = 0.10              # ancho del fundido donde el cuerpo toca un costado de la foto original

for e in json.load(open(f'{ent}/caras.json')):
    nombre = e['archivo'].rsplit('.', 1)[0]
    im = Image.open(f'{ent}/{nombre}.png').convert('RGBA')
    w, h = im.size
    a = im.getchannel('A')
    fx, fy, fw, fh = e['cara']
    cx, cy = (fx + fw / 2) * w, (1 - (fy + fh / 2)) * h       # centro de la cara en píxeles, desde arriba
    escala = CARA_ALTO * S / (fh * h)
    toca = {'abajo': a.crop((0, h - 2, w, h)).getextrema()[1] > 128, 'izq': a.crop((0, 0, 2, h)).getextrema()[1] > 128,
            'der': a.crop((w - 2, 0, w, h)).getextrema()[1] > 128}
    cara_cy = CARA_CY
    fundir_abajo = False
    if toca['abajo']:                                         # que el corte inferior caiga en el borde del lienzo, si se puede
        escala = min(max(escala, (S - CARA_CY * S) / (h - cy)), CARA_MAX * S / (fh * h))
        cara_cy = min(max(CARA_CY, (S - (h - cy) * escala) / S), CY_MAX)
        fundir_abajo = cara_cy * S + (h - cy) * escala < S - 1
    # fundido en los costados que el sujeto toca (el de abajo queda fuera del círculo)
    n = int(FUNDIDO * w)
    if n and (toca['izq'] or toca['der']):
        mascara = Image.new('L', (w, h), 255)
        rampa = Image.linear_gradient('L').rotate(90).resize((n, h))     # 0 a la izquierda, 255 a la derecha
        if toca['izq']:
            mascara.paste(rampa, (0, 0))
        if toca['der']:
            mascara.paste(rampa.transpose(Image.FLIP_LEFT_RIGHT), (w - n, 0))
        a = ImageChops.multiply(a, mascara)
    if fundir_abajo:
        nb = int(FUNDIDO_ABAJO * h)
        mascara = Image.new('L', (w, h), 255)
        mascara.paste(Image.linear_gradient('L').resize((w, nb)).transpose(Image.FLIP_TOP_BOTTOM), (0, h - nb))
        a = ImageChops.multiply(a, mascara)
    im.putalpha(a)
    nw, nh = round(w * escala), round(h * escala)
    grande = im.resize((nw, nh), Image.LANCZOS)
    lienzo = Image.new('RGBA', (S, S), (255, 255, 255, 255))
    ox, oy = round(S / 2 - cx * escala), round(cara_cy * S - cy * escala)
    lienzo.alpha_composite(grande, (max(ox, 0), max(oy, 0)), (max(-ox, 0), max(-oy, 0)))
    rgb = lienzo.convert('RGB')
    rgb.save(f'{sal}/{nombre}.jpg', quality=88, optimize=True, progressive=True)
    rgb.save(f'{sal}/{nombre}.webp', quality=84, method=6)
    print(f'{nombre:24s} origen {w}x{h}  escala {escala:4.2f}  cara {fh*h*escala/S:.2f}  cy {cara_cy:.2f}  fundido abajo {fundir_abajo}  toca {[k for k, v in toca.items() if v]}')
