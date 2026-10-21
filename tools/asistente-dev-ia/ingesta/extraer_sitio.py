"""Extrae el texto del sitio estático de la diplomatura en secciones citables.

Cada sección es un bloque de la página con su título, la URL pública y el ancla a la que lleva la cita:
las secciones de la portada (<section>/<article> con id), cada pregunta frecuente, cada módulo del plan y
las subpáginas partidas por títulos. Los bloques largos se cortan en tramos de ~220 palabras con el mismo
título. También lista los videos de YouTube embebidos en las páginas.

Uso: .venv/bin/python ingesta/extraer_sitio.py ~/Documents/GitHub/webLaboratorio/dev-ia
Escribe indice/secciones.json.
"""

import json
import pathlib
import re
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

RAIZ = pathlib.Path(__file__).resolve().parents[1]
BASE_URL = "/dev-ia/"
SUBPAGINAS = {"plan-de-estudios": "Plan de estudios", "aranceles": "Aranceles", "requisitos": "Requisitos",
              "destinatarios": "Destinatarios", "enfoque": "Enfoque", "por-que-elegirnos": "Por qué elegirnos",
              "inscripcion-dev-ia": "Inscripción"}
QUITAR = ["script", "style", "nav", "footer", "form", "noscript", "iframe", "svg", "select", "input", "textarea"]
# Secciones interactivas o de navegación que no aportan contenido
OMITIR_IDS = {"quiz-fit", "bordefino"}
MAX_PALABRAS = 220


def limpio(texto):
    return re.sub(r"\s+", " ", texto).strip()


def texto_de(el):
    """Texto legible del elemento: los bloques y los ítems de lista quedan separados."""
    partes = []
    for d in el.descendants:
        if isinstance(d, Comment):
            continue
        if isinstance(d, NavigableString):
            if d.parent and d.parent.name in QUITAR:
                continue
            partes.append(str(d))
        elif isinstance(d, Tag) and d.name in ("p", "li", "h1", "h2", "h3", "h4", "h5", "tr", "br", "div"):
            partes.append("\n")
    t = "".join(partes)
    lineas = [limpio(x) for x in t.split("\n")]
    return "\n".join(x for x in lineas if x)


def titulo_de(el):
    for h in el.find_all(["h1", "h2", "h3", "h4"], limit=3):
        t = limpio(h.get_text(" "))
        if len(t) > 2:
            return t
    return ""


def tramos(texto):
    """Corta por líneas en tramos de hasta MAX_PALABRAS palabras."""
    salida, actual, n = [], [], 0
    for linea in texto.split("\n"):
        w = len(linea.split())
        if actual and n + w > MAX_PALABRAS:
            salida.append("\n".join(actual))
            actual, n = [], 0
        actual.append(linea)
        n += w
    if actual:
        # Un último tramo muy corto se suma al anterior en lugar de quedar como sección propia
        if salida and n < 40:
            salida[-1] += "\n" + "\n".join(actual)
        else:
            salida.append("\n".join(actual))
    return salida


def agregar(secciones, titulo, url, ancla, texto, tipo="texto"):
    texto = texto.strip()
    if len(texto.split()) < 12:
        return
    for k, t in enumerate(tramos(texto)):
        secciones.append({"titulo": titulo + (f" ({k + 1})" if k else ""), "url": url, "ancla": ancla,
                          "tipo": tipo, "texto": t})


def portada(html, secciones):
    sopa = BeautifulSoup(html, "html.parser")
    for q in sopa.find_all(QUITAR):
        q.decompose()
    url = BASE_URL
    for bloque in sopa.find_all(["section", "article", "header"]):
        bid = bloque.get("id", "")
        if bid in OMITIR_IDS or bloque.find_parent(["section", "article"]):
            continue
        titulo = titulo_de(bloque) or "Diplomatura de Posgrado en IA Generativa en la Nube"
        # Acordeones: cada ítem es una sección propia (preguntas frecuentes y módulos del plan)
        for item in bloque.select(".accordion-item"):
            boton = item.select_one(".accordion-button")
            cuerpo = item.select_one(".accordion-collapse")
            if not boton or not cuerpo:
                continue
            pregunta = limpio(boton.get_text(" "))
            agregar(secciones, f"{titulo}: {pregunta}", url, cuerpo.get("id", bid), pregunta + "\n" + texto_de(cuerpo))
            item.decompose()
        agregar(secciones, titulo, url, bid, texto_de(bloque))


def subpagina(nombre, html, secciones):
    sopa = BeautifulSoup(html, "html.parser")
    for q in sopa.find_all(QUITAR):
        q.decompose()
    url = f"{BASE_URL}{nombre}/"
    cuerpo = sopa.find("main") or sopa.body
    pagina = SUBPAGINAS[nombre]
    # Partir por h2: cada h2 abre una sección hasta el siguiente h2. Se recorre todo el texto en orden
    # (los precios y datos sueltos suelen estar en div y span, no en párrafos).
    actual_t, actual_id, buf = pagina, "", []
    for d in cuerpo.descendants:
        if isinstance(d, Tag) and d.name == "h2":
            agregar(secciones, actual_t, url, actual_id, "\n".join(x for x in (limpio(l) for l in "".join(buf).split("\n")) if x))
            t = limpio(d.get_text(" "))
            actual_t = f"{pagina}: {t}" if t and t != pagina else pagina
            contenedor = d.find_parent(id=True)
            actual_id = d.get("id") or (contenedor.get("id") if contenedor and contenedor.name != "body" else "")
            buf = []
        elif isinstance(d, Tag) and d.name in ("p", "li", "h3", "h4", "h5", "tr", "br", "div", "dt", "dd"):
            buf.append("\n")
        elif isinstance(d, NavigableString) and not isinstance(d, Comment):
            if d.find_parent("h2") or d.find_parent("h1"):
                continue
            buf.append(str(d) + " ")
    agregar(secciones, actual_t, url, actual_id, "\n".join(x for x in (limpio(l) for l in "".join(buf).split("\n")) if x))


def videos(carpeta):
    vistos, salida = set(), []
    for f in [carpeta / "index.html"] + [carpeta / s / "index.html" for s in SUBPAGINAS]:
        sopa = BeautifulSoup(f.read_text(encoding="utf-8"), "html.parser")
        for ifr in sopa.find_all("iframe", src=re.compile(r"youtube(-nocookie)?\.com/embed/")):
            vid = re.search(r"/embed/([\w-]{6,})", ifr["src"]).group(1)
            if vid in vistos:
                continue
            vistos.add(vid)
            cont = ifr.find_parent(["section", "div"], id=True)
            titulo = ifr.get("title") or ""
            bloque = ifr.find_parent(["section", "article"])
            if bloque:
                titulo = titulo_de(bloque) or titulo
            salida.append({"youtube": vid, "titulo": limpio(titulo), "pagina": f.parent.name,
                           "ancla": cont.get("id") if cont else ""})
    return salida


def main():
    carpeta = pathlib.Path(sys.argv[1]).expanduser()
    secciones = []
    portada((carpeta / "index.html").read_text(encoding="utf-8"), secciones)
    for s in SUBPAGINAS:
        subpagina(s, (carpeta / s / "index.html").read_text(encoding="utf-8"), secciones)
    # Duplicados exactos (la portada repite textos de las subpáginas)
    vistos, unicas = set(), []
    for s in secciones:
        clave = s["texto"]
        if clave in vistos:
            continue
        vistos.add(clave)
        unicas.append(s)
    for i, s in enumerate(unicas):
        s["id"] = f"S{i + 1}"
    salida = {"secciones": unicas, "videos": videos(carpeta)}
    (RAIZ / "indice").mkdir(exist_ok=True)
    (RAIZ / "indice" / "secciones.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1), encoding="utf-8")
    palabras = sum(len(s["texto"].split()) for s in unicas)
    print(f"{len(unicas)} secciones, {palabras} palabras, {len(salida['videos'])} videos")


if __name__ == "__main__":
    main()
