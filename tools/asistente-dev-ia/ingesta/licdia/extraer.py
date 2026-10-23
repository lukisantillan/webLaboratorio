"""Extrae el contenido del sitio del laboratorio (licdia.unlu.edu.ar) en secciones citables para su asistente.

Fuentes: la portada (presentación, cada línea y proyecto con el texto de su ventana, cursos, carreras, equipo por
grupos y contacto), las publicaciones (los datos con los que se genera /publicaciones/, en tools/publicaciones), las
entradas del blog (tools/blog/entradas) y las páginas de proyectos. Los bloques largos se cortan en tramos con el mismo
título, como en la extracción de la diplomatura.

Uso: .venv/bin/python ingesta/licdia/extraer.py ~/Documents/GitHub/webLaboratorio
Escribe indice-licdia/secciones.json.
"""

import json
import pathlib
import re
import sys

from bs4 import BeautifulSoup, Comment, NavigableString, Tag

RAIZ = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ / "ingesta"))
from extraer_sitio import limpio, tramos  # noqa: E402  (mismas reglas de corte)


def texto_de(el):
    """Texto legible: los bloques y los ítems quedan separados, y los saltos de línea del HTML no cortan oraciones
    (a diferencia del extractor de la diplomatura, acá el HTML viene con líneas cortadas a mano)."""
    partes = []
    for d in el.descendants:
        if isinstance(d, Comment):
            continue
        if isinstance(d, NavigableString):
            if not (d.parent and d.parent.name in QUITAR):
                partes.append(re.sub(r"\s+", " ", str(d)))
        elif isinstance(d, Tag) and d.name in ("p", "li", "h1", "h2", "h3", "h4", "h5", "tr", "br", "div"):
            partes.append("\n")
    return "\n".join(x for x in (limpio(x) for x in "".join(partes).split("\n")) if x)

PAGINAS_PROYECTO = {"LLM": "Proyecto LLM en la nube", "ipc": "Proyecto IPC", "fitba-13c": "Proyecto fitba-13c",
                    "proyecto-enseñanza": "Proyecto de enseñanza de programación",
                    "proyecto-enseñanza/ia": "Curso de IA para escuelas secundarias",
                    "proyecto-enseñanza/juego": "Curso de videojuegos para escuelas secundarias",
                    "proyecto-enseñanza/web": "Curso de programación web para escuelas secundarias"}
QUITAR = ["script", "style", "nav", "footer", "form", "noscript", "iframe", "svg", "button"]


def sopa(ruta):
    s = BeautifulSoup(ruta.read_text(encoding="utf-8"), "html.parser")
    for t in s(QUITAR):
        t.decompose()
    return s


def agregar(salida, titulo, texto, url, ancla="", tipo="texto"):
    texto = texto.strip()
    if len(texto.split()) < 4:
        return
    for k, tramo in enumerate(tramos(texto)):
        salida.append({"titulo": titulo + (f" ({k + 1})" if k else ""), "url": url, "ancla": ancla, "tipo": tipo,
                       "texto": tramo})


def portada(sitio, salida):
    s = sopa(sitio / "index.html")
    pf = s.find(id="portfolio")
    intro = pf.find("h3", class_="section-subheading") if pf else None
    if intro:
        agregar(salida, "¿Qué hace el laboratorio?", limpio(intro.get_text(" ")), "/", "portfolio")
    # Cada línea y proyecto: el texto de su ventana (las tarjetas solo traen el título)
    for m in s.select("div.portfolio-modal"):
        cuerpo = m.find(class_="modal-body")
        if not cuerpo:
            continue
        t = limpio(cuerpo.find(["h2", "h3"]).get_text(" ")) if cuerpo.find(["h2", "h3"]) else ""
        cat = ""
        for li in cuerpo.select("ul.list-inline li"):
            if "Categoría" in li.get_text():
                cat = limpio(li.get_text(" ").replace("Categoría:", ""))
        for x in cuerpo.select("ul.list-inline"):
            x.decompose()
        nombre = ("Línea de I+D" if "Líneas" in cat else "Proyecto") + ": " + t.capitalize() if t.isupper() else \
            ("Línea de I+D" if "Líneas" in cat else "Proyecto") + ": " + t
        agregar(salida, nombre, texto_de(cuerpo), "/", m.get("id", ""))
    cur = s.find(id="cursosYcarreras")
    if cur:
        cursos = []
        for c in cur.select(".portfolio-caption"):
            cursos.append(limpio(c.get_text(" ")))
        agregar(salida, "Cursos, charlas, webinars y participaciones del laboratorio", "\n".join(cursos), "/", "cursosYcarreras")
        for d in cur.select("a.diplo-card"):
            agregar(salida, "Carrera: " + limpio(d.find(class_="diplo-card-titulo").get_text(" ")),
                    "Diplomatura de posgrado del laboratorio. " + texto_de(d) + "\nSitio: " + d.get("href", ""), "/", "cursosYcarreras")
        otras = [texto_de(c).replace("\n", " · ") + " (" + c.get("href", "") + ")" for c in cur.select("a.carrera-mini")]
        agregar(salida, "Otras carreras en las que participa el laboratorio", "\n".join(otras), "/", "cursosYcarreras")
    eq = s.find(id="team")
    if eq:
        grupo, personas = "Integrantes del laboratorio (UNLu)", {}
        for e in eq.select("h3.low-tittle, .team-member"):
            if e.name == "h3":
                t = limpio(e.get_text(" "))
                grupo = ("Tesistas actuales del laboratorio" if "Tesista" in t else "Pasantes del laboratorio" if "Pasante" in t
                         else "Colaboradores externos del laboratorio" if "Colaborador" in t else "Integrantes del laboratorio (UNLu)")
                continue
            personas.setdefault(grupo, []).append(texto_de(e).replace("\n", " · "))
        for g, lista in personas.items():
            agregar(salida, "Equipo: " + g, "\n".join(lista), "/", "team")
    ct = s.find(id="contact")
    if ct:
        agregar(salida, "Contacto y ubicación del laboratorio", texto_de(ct), "/", "contact")


def publicaciones(sitio, salida):
    sys.path.insert(0, str(sitio / "tools" / "publicaciones"))
    import enriquecer
    import gen_pubs_data as g
    for p in g.PUBS:
        meta = next((v for k, v in enriquecer.META.items() if k in p["titulo"]), None)
        partes = [f"{p.get('fecha') or p['anio']}. {p['tipo'].capitalize()}. {p.get('estado') or ''}".strip(" ."),
                  "Autores: " + p["autores"], "Presentado en: " + p["venue"]]
        if meta:
            partes.append(f"Área: {meta[0]}. Palabras clave: {', '.join(meta[3])}.")
        enlace = next((v for k, v in g.LINKS.items() if k in p["titulo"]), None) if hasattr(g, "LINKS") else None
        if isinstance(enlace, str):
            partes.append("Enlace: " + enlace)
        agregar(salida, "Publicación: " + p["titulo"], "\n".join(partes), "/publicaciones/", "publicaciones")


def blog(sitio, salida):
    for f in sorted((sitio / "tools" / "blog" / "entradas").glob("*.md"), reverse=True):
        m = re.match(r"---\n(.*?)\n---\n(.*)", f.read_text(encoding="utf-8"), re.S)
        meta = dict(linea.split(":", 1) for linea in m.group(1).splitlines() if ":" in linea)
        meta = {k.strip(): v.strip() for k, v in meta.items()}
        slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.stem)
        cuerpo = BeautifulSoup(re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", m.group(2)), "html.parser")
        for t in cuerpo(QUITAR):
            t.decompose()
        texto = f"{meta['fecha']} · {meta['autores']}. {meta['resumen']}\n" + texto_de(cuerpo)
        agregar(salida, "Blog: " + meta["titulo"], texto, f"/blog/{slug}/")


def paginas_proyecto(sitio, salida):
    for carpeta, nombre in PAGINAS_PROYECTO.items():
        ruta = sitio / carpeta / "index.html"
        if not ruta.exists():
            continue
        s = sopa(ruta)
        cab = s.find("header")
        titulo = limpio(cab.get_text(" ")) if cab and len(limpio(cab.get_text(" "))) < 140 else nombre
        if cab:
            cab.decompose()
        # Por bloques con título; lo que no está bajo un título va con el nombre del proyecto
        bloques = s.find_all(["section", "article"]) or [s.body]
        for b in bloques:
            h = b.find(["h2", "h3"])
            # sin signos de pregunta: "¿De qué trata el proyecto?" sin el nombre del proyecto no sirve de repregunta
            sub = limpio(h.get_text(" ")).strip("¿? ") if h else ""
            agregar(salida, titulo + (": " + sub.capitalize() if sub.isupper() else ": " + sub if sub else ""),
                    texto_de(b), f"/{carpeta}/", b.get("id", "") if b.name else "")


def main():
    sitio = pathlib.Path(sys.argv[1]).expanduser()
    salida = []
    portada(sitio, salida)
    publicaciones(sitio, salida)
    blog(sitio, salida)
    paginas_proyecto(sitio, salida)
    vistos, unicas = set(), []
    for s in salida:
        clave = s["texto"][:200]
        if clave not in vistos:
            vistos.add(clave)
            unicas.append(s)
    for i, s in enumerate(unicas, 1):
        s["id"] = f"S{i}"
    destino = RAIZ / "indice-licdia"
    destino.mkdir(exist_ok=True)
    (destino / "secciones.json").write_text(json.dumps({"secciones": unicas, "videos": []}, ensure_ascii=False, indent=1),
                                            encoding="utf-8")
    palabras = sum(len(s["texto"].split()) for s in unicas)
    print(f"{len(unicas)} secciones, {palabras} palabras")


if __name__ == "__main__":
    main()
