#!/usr/bin/env python3
"""Renderiza publicaciones/index.html con el panel de filtros completo.

Los datos vienen de gen_pubs_data.py (PUBS, PROXIMAS, LINKS) y los metadatos
extra de enriquecer.py (area, sede, idioma, palabras clave).
"""

import html
import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).parent))

import enriquecer as E  # noqa: E402
from gen_pubs_data import PROXIMAS, PUBS, buscar_citas, buscar_link  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
TIPO_LABEL = {
    "congreso": "Congreso",
    "revista": "Revista",
    "poster": "Póster",
    "libro": "Libro",
}
IDIOMA_LABEL = {"es": "Español", "en": "Inglés"}


def esc(s):
    return html.escape(s, quote=False)


def attr(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------- enriquecido
for p in PUBS:
    meta = E.buscar_meta(p["titulo"])
    if meta is None:
        raise SystemExit(f"sin metadatos: {p['titulo'][:60]}")
    area, idioma, sede, tags = meta
    p["area"] = area
    p["idioma"] = idioma
    p["sede"] = sede or E.sede_desde_venue(p["venue"])
    p["tags"] = tags
    p["autores_lista"] = E.autores_lista(p["autores"])
    p["link"] = buscar_link(p["titulo"], p.get("venue", ""))
    p["citas"] = buscar_citas(p["titulo"])

for p in PROXIMAS:
    area, idioma, tags = E.buscar_meta(p["titulo"], E.META_PROXIMAS)
    p["area"] = area
    p["idioma"] = idioma
    p["tags"] = tags


# ------------------------------------------------------------------- facetas
anios = sorted({p["anio"] for p in PUBS}, reverse=True)
areas = sorted(Counter(p["area"] for p in PUBS).items(), key=lambda kv: (-kv[1], kv[0]))
sedes = sorted(Counter(p["sede"] for p in PUBS).items(), key=lambda kv: (-kv[1], kv[0]))
autores = Counter()
for p in PUBS:
    for a in p["autores_lista"]:
        autores[a] += 1
autores_orden = sorted(autores.items(), key=lambda kv: (-kv[1], E.apellido(kv[0])))
tags_todos = sorted({t for p in PUBS for t in p["tags"]})

total = len(PUBS)
n_congreso = sum(1 for p in PUBS if p["tipo"] == "congreso")
n_revista = sum(1 for p in PUBS if p["tipo"] == "revista")
n_acceso = sum(1 for p in PUBS if p.get("link") or p.get("pdf"))


# -------------------------------------------------------------------- tarjeta
def card(p):
    badges = [
        f'<span class="pub-badge pub-badge--{p["tipo"]}">{TIPO_LABEL[p["tipo"]]}</span>'
    ]
    if p.get("estado"):
        badges.append(
            f'<span class="pub-badge pub-badge--estado">{esc(p["estado"])}</span>'
        )
    if p.get("citas"):
        badges.append(
            f'<span class="pub-badge pub-badge--citas" title="Citas registradas en OpenAlex / Crossref">'
            f'<i class="fas fa-quote-left"></i> {p["citas"]} {"cita" if p["citas"] == 1 else "citas"}</span>'
        )

    acciones = []
    if p.get("link"):
        url, etiqueta = p["link"]
        acciones.append(
            f'<a class="pub-link" href="{url}" target="_blank" rel="noopener">'
            f'<i class="fas fa-up-right-from-square"></i> {esc(etiqueta)}</a>'
        )
    if p.get("pdf"):
        acciones.append(
            f'<a class="pub-link" href="{p["pdf"]}" target="_blank" rel="noopener">'
            f'<i class="fas fa-file-pdf"></i> Póster (PDF)</a>'
        )
    acciones.append(
        '<button type="button" class="pub-copiar" data-cita="'
        + attr(
            f"{p['autores']} ({p['anio']}). {p['titulo']}. {html.unescape(p['venue'])}."
        )
        + '"><i class="fas fa-quote-right"></i> Copiar cita</button>'
    )

    tags = "".join(
        f'<button type="button" class="pub-tag" data-tag="{attr(t)}">{esc(t)}</button>'
        for t in p["tags"]
    )
    nota = (
        f'\n                    <p class="pub-nota">{esc(p["nota"])}</p>'
        if p.get("nota")
        else ""
    )

    haystack = " ".join(
        [
            p["titulo"],
            p["autores"],
            html.unescape(p["venue"]),
            p["area"],
            p["sede"],
            p.get("nota", ""),
            " ".join(p["tags"]),
        ]
    ).lower()

    return f"""                <article class="pub-item" data-anio="{p["anio"]}" data-tipo="{p["tipo"]}"
                    data-area="{attr(p["area"])}" data-sede="{attr(p["sede"])}" data-idioma="{p["idioma"]}"
                    data-acceso="{"si" if (p.get("link") or p.get("pdf")) else "no"}"
                    data-citas="{p.get("citas", 0)}"
                    data-autores="{attr("|".join(p["autores_lista"]))}"
                    data-tags="{attr("|".join(p["tags"]))}"
                    data-titulo="{attr(p["titulo"][:120].lower())}"
                    data-buscar="{attr(haystack)}">
                    <div class="pub-meta">
                        <span class="pub-fecha">{esc(p["fecha"])}</span>
                        {" ".join(badges)}
                        <span class="pub-area">{esc(p["area"])}</span>
                    </div>
                    <div class="pub-cuerpo">
                        <h3 class="pub-titulo">{p["titulo"]}</h3>
                        <p class="pub-autores">{p["autores"]}</p>
                        <p class="pub-venue">{p["venue"]}</p>{nota}
                        <div class="pub-tags">{tags}</div>
                        <div class="pub-acciones">{"".join(acciones)}</div>
                    </div>
                </article>
"""


def card_proxima(p):
    tags = "".join(
        f'<span class="pub-tag pub-tag--plano">{esc(t)}</span>' for t in p["tags"]
    )
    return f"""                <article class="pub-item pub-item--proxima">
                    <div class="pub-meta">
                        <span class="pub-fecha">En preparación</span>
                        <span class="pub-badge pub-badge--proxima">Sede y fecha a confirmar</span>
                        <span class="pub-area">{esc(p["area"])}</span>
                    </div>
                    <div class="pub-cuerpo">
                        <h3 class="pub-titulo">{p["titulo"]}</h3>
                        <p class="pub-autores">{p["autores"]}</p>
                        <p class="pub-venue">Eje temático: {esc(p["eje"])}</p>
                        <p class="pub-resumen">{esc(p["resumen"])}</p>
                        <div class="pub-tags">{tags}</div>
                    </div>
                </article>
"""


# ---------------------------------------------------------------------- UI
def chips(nombre, items, label_todos):
    out = [
        f'<button type="button" class="pub-chip activo" data-filtro="{nombre}" data-valor="">{label_todos}</button>'
    ]
    for valor, etiqueta, cuenta in items:
        out.append(
            f'<button type="button" class="pub-chip" data-filtro="{nombre}" data-valor="{attr(valor)}">'
            f'{esc(etiqueta)} <span class="pub-chip-n">{cuenta}</span></button>'
        )
    return "\n                    ".join(out)


cuenta_tipo = Counter(p["tipo"] for p in PUBS)
chips_tipo = chips(
    "tipo",
    [
        (t, TIPO_LABEL[t], cuenta_tipo[t])
        for t in ["congreso", "revista", "poster", "libro"]
        if cuenta_tipo[t]
    ],
    "Todos los tipos",
)
cuenta_anio = Counter(p["anio"] for p in PUBS)
chips_anio = chips(
    "anio", [(str(a), str(a), cuenta_anio[a]) for a in anios], "Todos los años"
)
cuenta_idioma = Counter(p["idioma"] for p in PUBS)
chips_idioma = chips(
    "idioma",
    [
        (i, IDIOMA_LABEL[i], c)
        for i, c in sorted(cuenta_idioma.items(), key=lambda kv: -kv[1])
    ],
    "Ambos idiomas",
)

opciones_area = "\n                        ".join(
    f'<option value="{attr(a)}">{esc(a)} ({c})</option>' for a, c in areas
)
opciones_sede = "\n                        ".join(
    f'<option value="{attr(s)}">{esc(s)} ({c})</option>' for s, c in sedes
)
opciones_autor = "\n                        ".join(
    f'<option value="{attr(a)}">{esc(a)} ({c})</option>' for a, c in autores_orden
)
opciones_tag = "\n                        ".join(
    f'<option value="{attr(t)}">{esc(t)}</option>' for t in tags_todos
)

items_html = "".join(card(p) for p in PUBS)


def jsonld_item(p, pos):
    tipo = {"revista": "ScholarlyArticle", "libro": "Book"}.get(p["tipo"], "ScholarlyArticle")
    it = {
        "@type": tipo,
        "position": pos,
        "name": html.unescape(p["titulo"]),
        "author": [{"@type": "Person", "name": a} for a in p["autores_lista"]],
        "datePublished": str(p["anio"]),
        "inLanguage": p["idioma"],
        "keywords": ", ".join(p["tags"]),
        "isPartOf": {"@type": "Periodical" if p["tipo"] == "revista" else "Event",
                     "name": html.unescape(p["venue"])},
    }
    if p.get("link"):
        it["url"] = p["link"][0]
        if p["link"][0].startswith("https://doi.org/"):
            it["identifier"] = p["link"][0].replace("https://doi.org/", "doi:")
    return it


jsonld = json.dumps({
    "@context": "https://schema.org",
    "@type": "ItemList",
    "name": "Publicaciones del LICDIA, Universidad Nacional de Luján",
    "url": "https://licdia.unlu.edu.ar/publicaciones/",
    "numberOfItems": len(PUBS),
    "itemListElement": [jsonld_item(p, i) for i, p in enumerate(PUBS, 1)],
}, ensure_ascii=False)
proximas_html = "".join(card_proxima(p) for p in PROXIMAS)

HTML = f"""<!DOCTYPE html>
<html lang="es">

<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no" />
    <meta name="description"
        content="Producción científica del Laboratorio de Investigación en Ciencia de Datos e Inteligencia Artificial (LICDIA) del Departamento de Ciencias Básicas de la UNLu: artículos, ponencias, pósteres y libros, con filtros por año, área, autor, sede, idioma y palabras clave." />
    <meta name="author" content="LICDIA UNLu" />
    <title>Publicaciones - LICDIA UNLu</title>
    <meta property="og:title" content="Publicaciones - LICDIA UNLu" />
    <meta property="og:description"
        content="Producción científica del Laboratorio de Investigación en Ciencia de Datos e Inteligencia Artificial de la Universidad Nacional de Luján." />
    <meta property="og:image" content="https://licdia.unlu.edu.ar/assets/img/og-default.jpg" />
    <meta property="og:url" content="https://licdia.unlu.edu.ar/publicaciones/" />
    <meta property="og:type" content="website" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="Publicaciones - LICDIA UNLu" />
    <meta name="twitter:description"
        content="Producción científica del Laboratorio de Investigación en Ciencia de Datos e Inteligencia Artificial de la Universidad Nacional de Luján." />
    <meta name="twitter:image" content="https://licdia.unlu.edu.ar/assets/img/og-default.jpg" />
    <link rel="canonical" href="https://licdia.unlu.edu.ar/publicaciones/" />
    <!-- Datos estructurados: lista de articulos para buscadores (schema.org) -->
    <script type="application/ld+json">{jsonld}</script>
    <!-- Favicon-->
    <link rel="icon" type="image/x-icon" href="../assets/img/logo.ico" />
    <!-- Font Awesome icons (free version)-->
    <script src="https://use.fontawesome.com/releases/v6.3.0/js/all.js" crossorigin="anonymous"></script>
    <!-- Google fonts-->
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel="stylesheet" type="text/css" />
    <link href="https://fonts.googleapis.com/css?family=Roboto+Slab:400,100,300,700" rel="stylesheet" type="text/css" />
    <!-- Core theme CSS (includes Bootstrap)-->
    <link href="../css/styles.css" rel="stylesheet" />
    <link href="../css/style2.css" rel="stylesheet" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
    <style>
        .pub-intro {{ max-width: 60rem; margin: 0 auto 2rem; text-align: center; }}
        .pub-stats {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem; margin-top: 1.5rem; }}
        .pub-stat {{ min-width: 7rem; }}
        .pub-stat strong {{ display: block; font-family: 'Montserrat', sans-serif; font-size: 2rem; line-height: 1; }}
        .pub-stat span {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; color: #6c757d; }}

        .pub-panel {{ background: #f8f9fa; border: 1px solid #e9ecef; border-radius: .6rem;
            padding: 1.25rem 1.25rem .9rem; margin-bottom: 1.5rem; }}
        .pub-buscador {{ position: relative; margin-bottom: 1rem; }}
        .pub-buscador input {{ width: 100%; padding: .7rem 1rem .7rem 2.4rem; border: 1px solid #ced4da;
            border-radius: 2rem; font-size: .95rem; background: #fff; }}
        .pub-buscador i {{ position: absolute; left: .95rem; top: 50%; transform: translateY(-50%); color: #adb5bd; }}
        .pub-buscador input:focus {{ outline: 2px solid #0d6efd; outline-offset: 1px; }}

        .pub-selects {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr));
            gap: .75rem; margin-bottom: 1rem; }}
        .pub-campo label {{ display: block; font-size: .7rem; text-transform: uppercase; letter-spacing: .06em;
            color: #6c757d; font-weight: 700; margin-bottom: .22rem; }}
        .pub-campo select {{ width: 100%; padding: .45rem .6rem; border: 1px solid #ced4da; border-radius: .35rem;
            font-size: .87rem; background: #fff; }}
        .pub-campo select:focus {{ outline: 2px solid #0d6efd; outline-offset: 1px; }}

        .pub-grupo-chips {{ margin-bottom: .55rem; }}
        .pub-grupo-chips > span.pub-grupo-label {{ display: inline-block; font-size: .7rem; text-transform: uppercase;
            letter-spacing: .06em; color: #6c757d; font-weight: 700; margin-right: .4rem; }}
        .pub-chip {{ border: 1px solid #ced4da; background: #fff; color: #495057; border-radius: 2rem;
            padding: .25rem .75rem; font-size: .78rem; cursor: pointer; margin: 0 .25rem .3rem 0; }}
        .pub-chip:hover {{ border-color: #0d6efd; color: #0d6efd; }}
        .pub-chip.activo {{ background: #0d6efd; border-color: #0d6efd; color: #fff; }}
        .pub-chip-n {{ opacity: .6; font-size: .72rem; }}

        .pub-barra {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between;
            gap: .75rem; padding-top: .6rem; border-top: 1px solid #e9ecef; }}
        .pub-contador {{ font-size: .85rem; color: #495057; }}
        .pub-contador strong {{ color: #0d6efd; }}
        .pub-acciones-barra {{ display: flex; flex-wrap: wrap; gap: .5rem; }}
        .pub-boton {{ border: 1px solid #ced4da; background: #fff; color: #495057; border-radius: .35rem;
            padding: .3rem .75rem; font-size: .8rem; cursor: pointer; }}
        .pub-boton:hover {{ border-color: #0d6efd; color: #0d6efd; }}
        .pub-boton--limpiar[hidden] {{ display: none !important; }}

        .pub-sep {{ font-family: 'Montserrat', sans-serif; font-size: 1.25rem; text-transform: uppercase;
            letter-spacing: .06em; border-bottom: 2px solid #dee2e6; padding-bottom: .4rem; margin: 2.2rem 0 1rem; }}
        .pub-item {{ display: flex; flex-wrap: wrap; gap: 1rem; padding: 1.1rem 0; border-bottom: 1px solid #eceef0; }}
        .pub-meta {{ flex: 0 0 11rem; display: flex; flex-direction: column; gap: .35rem; align-items: flex-start; }}
        .pub-cuerpo {{ flex: 1 1 20rem; min-width: 0; }}
        .pub-fecha {{ font-size: .8rem; text-transform: uppercase; letter-spacing: .05em; color: #6c757d; }}
        .pub-area {{ font-size: .74rem; color: #495057; }}
        .pub-badge {{ display: inline-block; font-size: .68rem; text-transform: uppercase; letter-spacing: .05em;
            padding: .18rem .5rem; border-radius: .25rem; }}
        .pub-badge--congreso {{ background: #e7f1ff; color: #0a58ca; }}
        .pub-badge--revista {{ background: #e6f7ef; color: #0f6848; }}
        .pub-badge--poster {{ background: #fdf1e3; color: #9a5b00; }}
        .pub-badge--libro {{ background: #f0e9fb; color: #5b32a8; }}
        .pub-badge--estado {{ background: #f1f3f5; color: #495057; }}
        .pub-badge--proxima {{ background: #fff3cd; color: #7a5b00; }}
        .pub-badge--citas {{ background: #fff0f3; color: #a3244a; }}
        .pub-perfiles {{ display: flex; flex-wrap: wrap; justify-content: center; gap: .5rem 1.25rem;
            margin-top: 1.1rem; font-size: .82rem; }}
        .pub-perfiles a {{ color: #495057; text-decoration: none; }}
        .pub-perfiles a:hover {{ color: #0d6efd; }}
        .pub-perfiles i {{ color: #a6ce39; margin-right: .25rem; }}
        .pub-titulo {{ font-family: 'Roboto Slab', serif; font-size: 1.02rem; font-weight: 700; line-height: 1.4; margin: 0 0 .35rem; }}
        .pub-autores {{ margin: 0 0 .2rem; font-size: .92rem; color: #343a40; }}
        .pub-venue {{ margin: 0; font-size: .88rem; color: #6c757d; }}
        .pub-nota {{ margin: .3rem 0 0; font-size: .85rem; color: #6c757d; font-style: italic; }}
        .pub-resumen {{ margin: .6rem 0 0; font-size: .9rem; color: #495057; }}
        .pub-tags {{ margin-top: .5rem; }}
        .pub-tag {{ border: 1px solid #e3e6ea; background: #f8f9fa; color: #56606a; border-radius: .25rem;
            padding: .12rem .45rem; font-size: .73rem; cursor: pointer; margin: 0 .25rem .25rem 0; }}
        .pub-tag:hover {{ border-color: #0d6efd; color: #0d6efd; }}
        .pub-tag--plano {{ cursor: default; display: inline-block; }}
        .pub-acciones {{ margin-top: .45rem; display: flex; flex-wrap: wrap; gap: 1rem; align-items: center; }}
        .pub-link {{ font-size: .82rem; font-weight: 700; text-decoration: none; color: #0a58ca; }}
        .pub-link:hover {{ text-decoration: underline; }}
        .pub-copiar {{ border: 0; background: none; padding: 0; color: #6c757d; font-size: .8rem; cursor: pointer; }}
        .pub-copiar:hover {{ color: #0d6efd; }}
        .pub-item--proxima {{ background: #fffdf5; border-left: 3px solid #ffc107; padding-left: 1rem; }}
        .pub-vacio {{ text-align: center; color: #6c757d; padding: 2.5rem 0; }}

        @media (max-width: 767px) {{
            .pub-chip {{ padding: .45rem .85rem; font-size: .8rem; }}
            .pub-tag {{ padding: .3rem .55rem; }}
            .pub-meta {{ flex: 1 1 100%; flex-direction: row; flex-wrap: wrap; align-items: center; }}
            .pub-sep {{ font-size: 1.1rem; }}
            .pub-panel {{ padding: 1rem .85rem .7rem; }}
        }}
    </style>
</head>

<body id="page-top">
    <!-- Navigation-->
    <nav class="navbar navbar-expand-lg navbar-dark fixed-top" id="mainNav">
        <div class="container">
            <a class="navbar-brand efect" href="../"><img src="../assets/img/logo.ico" alt="LICDIA" /></a>
            <a class="navbar-brand efect" href="../"><img src="../assets/img/depto.ico" alt="Departamento de Ciencias Basicas" /></a>
            <a class="navbar-brand efect" href="../"><img src="../assets/img/unlu.ico" alt="UNLu" /></a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarResponsive"
                aria-controls="navbarResponsive" aria-expanded="false" aria-label="Toggle navigation">
                Menu
                <i class="fas fa-bars ms-1"></i>
            </button>
            <div class="collapse navbar-collapse" id="navbarResponsive">
                <ul class="navbar-nav text-uppercase ms-auto py-4 py-lg-0">
                    <li class="nav-item"><a class="nav-link" href="../">Inicio</a></li>
                    <li class="nav-item"><a class="nav-link" href="../#portfolio">¿Qué hacemos?</a></li>
                    <li class="nav-item"><a class="nav-link" href="./">Publicaciones</a></li>
                    <li class="nav-item"><a class="nav-link" href="../#team">Equipo y colaboradores</a></li>
                    <li class="nav-item"><a class="nav-link" href="../#contact">Contacto</a></li>
                </ul>
            </div>
        </div>
    </nav>
    <!-- Masthead-->
    <header class="masthead efect fondoPublicaciones"
        style="--bg-img: url(../assets/img/banner-publicaciones.webp);">
        <div class="container overlay">
            <div class="masthead-heading text-uppercase text-center">Publicaciones</div>
        </div>
    </header>

    <section class="page-section" id="publicaciones">
        <div class="container">
            <div class="pub-intro">
                <h2 class="section-heading text-uppercase">Producción científica del LICDIA</h2>
                <p class="text-muted">
                    Artículos en revistas, ponencias en congresos, pósteres y libros producidos por el Laboratorio de
                    Investigación en Ciencia de Datos &amp; Inteligencia Artificial del Departamento de Ciencias
                    Básicas de la Universidad Nacional de Luján, junto a sus grupos e instituciones asociadas.
                </p>
                <div class="pub-stats">
                    <div class="pub-stat"><strong>{total}</strong><span>Publicaciones</span></div>
                    <div class="pub-stat"><strong>{n_congreso}</strong><span>En congresos</span></div>
                    <div class="pub-stat"><strong>{n_revista}</strong><span>En revistas</span></div>
                    <div class="pub-stat"><strong>{len(autores)}</strong><span>Autores</span></div>
                    <div class="pub-stat"><strong>{anios[-1]}-{anios[0]}</strong><span>Período</span></div>
                </div>
                <div class="pub-perfiles">
                    <a href="https://orcid.org/0000-0001-9291-3066" target="_blank" rel="noopener"><i class="fab fa-orcid"></i>Juan Manuel Fernández</a>
                    <a href="https://orcid.org/0000-0003-1337-6456" target="_blank" rel="noopener"><i class="fab fa-orcid"></i>Mario Oloriz</a>
                    <a href="https://orcid.org/0000-0003-4865-0603" target="_blank" rel="noopener"><i class="fab fa-orcid"></i>Rosana Matuk Herrera</a>
                </div>
            </div>

            <!--
                PANEL DE FILTROS
                Todo el filtrado ocurre en el navegador sobre el markup estatico de abajo: cada
                <article> lleva sus facetas en data-* y el script solo muestra u oculta. No hay
                backend ni dependencias nuevas, y las entradas siguen en el HTML para indexacion.
                El estado se refleja en la query string, asi que una busqueda filtrada se puede
                compartir por link.
            -->
            <div class="pub-panel">
                <div class="pub-buscador">
                    <i class="fas fa-magnifying-glass"></i>
                    <label class="visually-hidden" for="pubBuscar">Buscar publicaciones</label>
                    <input type="search" id="pubBuscar"
                        placeholder="Buscar por título, autor, congreso, área o palabra clave...">
                </div>

                <div class="pub-selects">
                    <div class="pub-campo">
                        <label for="pubArea">Área</label>
                        <select id="pubArea" data-filtro="area">
                            <option value="">Todas las áreas</option>
                        {opciones_area}
                        </select>
                    </div>
                    <div class="pub-campo">
                        <label for="pubAutor">Autor</label>
                        <select id="pubAutor" data-filtro="autor">
                            <option value="">Todos los autores</option>
                        {opciones_autor}
                        </select>
                    </div>
                    <div class="pub-campo">
                        <label for="pubSede">Sede</label>
                        <select id="pubSede" data-filtro="sede">
                            <option value="">Todas las sedes</option>
                        {opciones_sede}
                        </select>
                    </div>
                    <div class="pub-campo">
                        <label for="pubTag">Palabra clave</label>
                        <select id="pubTag" data-filtro="tag">
                            <option value="">Todas las palabras clave</option>
                        {opciones_tag}
                        </select>
                    </div>
                    <div class="pub-campo">
                        <label for="pubOrden">Ordenar por</label>
                        <select id="pubOrden">
                            <option value="anio-desc">Año, más reciente primero</option>
                            <option value="anio-asc">Año, más antiguo primero</option>
                            <option value="titulo-asc">Título, A-Z</option>
                            <option value="autor-asc">Primer autor, A-Z</option>
                            <option value="citas-desc">Más citadas primero</option>
                        </select>
                    </div>
                </div>

                <div class="pub-grupo-chips">
                    <span class="pub-grupo-label">Tipo</span>
                    {chips_tipo}
                </div>
                <div class="pub-grupo-chips">
                    <span class="pub-grupo-label">Idioma</span>
                    {chips_idioma}
                    <button type="button" class="pub-chip" data-filtro="acceso" data-valor="si">
                        Con texto disponible <span class="pub-chip-n">{n_acceso}</span></button>
                </div>
                <div class="pub-grupo-chips">
                    <span class="pub-grupo-label">Año</span>
                    {chips_anio}
                </div>

                <div class="pub-barra">
                    <span class="pub-contador" id="pubContador" aria-live="polite">
                        Mostrando <strong>{total}</strong> de {total} publicaciones</span>
                    <span class="pub-acciones-barra">
                        <button type="button" class="pub-boton pub-boton--limpiar" id="pubLimpiar" hidden>
                            <i class="fas fa-xmark"></i> Limpiar filtros</button>
                        <button type="button" class="pub-boton" id="pubBibtex">
                            <i class="fas fa-download"></i> Descargar BibTeX</button>
                    </span>
                </div>
            </div>

            <!--
                COMO AGREGAR UNA PUBLICACION
                Copiar un bloque <article class="pub-item"> completo y editarlo. Los data-* son
                lo que consumen los filtros, el buscador y el orden; si alguno falta, esa entrada
                queda fuera de la faceta correspondiente:
                  data-anio    ano (tambien arma los separadores por ano)
                  data-tipo    congreso | revista | poster | libro
                  data-area    una de las areas que aparecen en el select #pubArea
                  data-sede    congreso o revista, como figura en #pubSede
                  data-idioma  es | en
                  data-acceso  si | no  (si tiene enlace o PDF)
                  data-autores autores separados por |, en el mismo formato que #pubAutor
                  data-tags    palabras clave separadas por |
                  data-titulo  titulo en minusculas, lo usa el orden alfabetico
                  data-buscar  todo lo anterior junto en minusculas, lo usa el buscador
                Si sumas un area, sede, autor o palabra clave nuevos, agregar tambien la <option>
                al select correspondiente, y el chip si es un ano nuevo.
            -->
            <div id="pubListado">
{items_html}            </div>
            <p class="pub-vacio" id="pubVacio" hidden>
                No hay publicaciones que coincidan con los filtros aplicados.</p>
        </div>
    </section>

    <section class="page-section bg-light" id="proximas">
        <div class="container">
            <div class="text-center">
                <h2 class="section-heading text-uppercase">Próximas presentaciones</h2>
                <p class="text-muted">Trabajos en preparación, pendientes de confirmación de sede y fecha.</p>
            </div>
{proximas_html}        </div>
    </section>

    <footer class="footer bg-dark text-white py-4 mt-2">
        <div class="container text-center small">
            <p class="mb-2">
                Copyright &copy; 2026 | Laboratorio de Investigación en Ciencia de Datos &amp; Inteligencia
                Artificial de la Universidad de Luján
                <a href="https://resoluciones.unlu.edu.ar/documento.frame.php?cod=128241" target="_blank"
                    class="text-decoration-none text-info">
                    [Disposición del Grupo de Investigación]
                </a>
                <a href="https://drive.google.com/file/d/1AddV4FMq70bOO4REUgAVppe5i4Vw9h_W/view" target="_blank"
                    class="text-decoration-none text-info">
                    [Resolución del Laboratorio]
                </a>
                - Argentina. Todos los derechos reservados.
            </p>
        </div>
    </footer>

    <!-- Bootstrap core JS-->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
    <!-- Core theme JS-->
    <script src="../js/scripts.js"></script>
    <script>
        (function () {{
            var listado = document.getElementById('pubListado');
            var items = Array.prototype.slice.call(listado.querySelectorAll('.pub-item'));
            var vacio = document.getElementById('pubVacio');
            var contador = document.getElementById('pubContador');
            var limpiar = document.getElementById('pubLimpiar');
            var total = items.length;

            var estado = {{
                texto: '', tipo: '', anio: '', idioma: '', acceso: '',
                area: '', autor: '', sede: '', tag: '', orden: 'anio-desc'
            }};

            // ---- orden -------------------------------------------------------
            function clave(it, modo) {{
                if (modo === 'titulo-asc') return it.dataset.titulo;
                if (modo === 'autor-asc') return (it.dataset.autores.split('|')[0] || '').toLowerCase();
                if (modo === 'citas-desc') return String(1000 - parseInt(it.dataset.citas || '0', 10)).padStart(4, '0');
                return it.dataset.anio;
            }}

            function ordenar() {{
                var modo = estado.orden;
                var copia = items.slice().sort(function (a, b) {{
                    var ka = clave(a, modo), kb = clave(b, modo);
                    if (ka === kb) return a.dataset.titulo < b.dataset.titulo ? -1 : 1;
                    if (modo === 'anio-desc') return kb.localeCompare(ka);
                    return ka.localeCompare(kb);
                }});
                copia.forEach(function (it) {{ listado.appendChild(it); }});
            }}

            // ---- separadores por año ----------------------------------------
            function separadores() {{
                listado.querySelectorAll('.pub-sep').forEach(function (s) {{ s.remove(); }});
                if (estado.orden.indexOf('anio') !== 0) return;
                var ultimo = null;
                items.forEach(function (it) {{
                    if (it.hidden) return;
                    if (it.dataset.anio !== ultimo) {{
                        ultimo = it.dataset.anio;
                        var sep = document.createElement('div');
                        sep.className = 'pub-sep';
                        sep.textContent = ultimo;
                        listado.insertBefore(sep, it);
                    }}
                }});
            }}

            // ---- filtrado ----------------------------------------------------
            function pasa(it) {{
                if (estado.tipo && it.dataset.tipo !== estado.tipo) return false;
                if (estado.anio && it.dataset.anio !== estado.anio) return false;
                if (estado.idioma && it.dataset.idioma !== estado.idioma) return false;
                if (estado.acceso && it.dataset.acceso !== estado.acceso) return false;
                if (estado.area && it.dataset.area !== estado.area) return false;
                if (estado.sede && it.dataset.sede !== estado.sede) return false;
                if (estado.autor && it.dataset.autores.split('|').indexOf(estado.autor) === -1) return false;
                if (estado.tag && it.dataset.tags.split('|').indexOf(estado.tag) === -1) return false;
                if (estado.texto) {{
                    // todas las palabras tienen que aparecer, en cualquier orden
                    var partes = estado.texto.split(/\\s+/);
                    for (var i = 0; i < partes.length; i++) {{
                        if (it.dataset.buscar.indexOf(partes[i]) === -1) return false;
                    }}
                }}
                return true;
            }}

            function hayFiltros() {{
                return estado.texto || estado.tipo || estado.anio || estado.idioma ||
                       estado.acceso || estado.area || estado.autor || estado.sede || estado.tag;
            }}

            function aplicar(guardarUrl) {{
                var visibles = 0;
                items.forEach(function (it) {{
                    var ok = pasa(it);
                    it.hidden = !ok;
                    if (ok) visibles++;
                }});
                ordenar();
                separadores();
                vacio.hidden = visibles !== 0;
                contador.innerHTML = 'Mostrando <strong>' + visibles + '</strong> de ' + total + ' publicaciones';
                limpiar.hidden = !hayFiltros();
                if (guardarUrl !== false) sincronizarUrl();
            }}

            // ---- estado en la URL -------------------------------------------
            function sincronizarUrl() {{
                var q = new URLSearchParams();
                Object.keys(estado).forEach(function (k) {{
                    if (estado[k] && !(k === 'orden' && estado[k] === 'anio-desc')) q.set(k, estado[k]);
                }});
                var s = q.toString();
                history.replaceState(null, '', s ? '?' + s : location.pathname);
            }}

            function leerUrl() {{
                var q = new URLSearchParams(location.search);
                Object.keys(estado).forEach(function (k) {{
                    if (q.has(k)) estado[k] = q.get(k);
                }});
            }}

            // ---- sincronizar controles con el estado -------------------------
            function pintarControles() {{
                document.querySelectorAll('.pub-chip[data-filtro]').forEach(function (chip) {{
                    var f = chip.dataset.filtro;
                    if (f === 'acceso') {{
                        chip.classList.toggle('activo', estado.acceso === chip.dataset.valor);
                    }} else {{
                        chip.classList.toggle('activo', estado[f] === chip.dataset.valor);
                    }}
                }});
                document.querySelectorAll('select[data-filtro]').forEach(function (sel) {{
                    sel.value = estado[sel.dataset.filtro] || '';
                }});
                document.getElementById('pubOrden').value = estado.orden;
                document.getElementById('pubBuscar').value = estado.texto;
            }}

            // ---- eventos -----------------------------------------------------
            document.querySelectorAll('.pub-chip[data-filtro]').forEach(function (chip) {{
                chip.addEventListener('click', function () {{
                    var f = chip.dataset.filtro;
                    // el chip de acceso funciona como interruptor
                    estado[f] = (f === 'acceso' && estado[f] === chip.dataset.valor) ? '' : chip.dataset.valor;
                    pintarControles();
                    aplicar();
                }});
            }});

            document.querySelectorAll('select[data-filtro]').forEach(function (sel) {{
                sel.addEventListener('change', function () {{
                    estado[sel.dataset.filtro] = sel.value;
                    aplicar();
                }});
            }});

            document.getElementById('pubOrden').addEventListener('change', function (e) {{
                estado.orden = e.target.value;
                aplicar();
            }});

            var debounce;
            document.getElementById('pubBuscar').addEventListener('input', function (e) {{
                clearTimeout(debounce);
                var v = e.target.value.trim().toLowerCase();
                debounce = setTimeout(function () {{ estado.texto = v; aplicar(); }}, 140);
            }});

            listado.addEventListener('click', function (e) {{
                var tag = e.target.closest('.pub-tag[data-tag]');
                if (tag) {{
                    estado.tag = estado.tag === tag.dataset.tag ? '' : tag.dataset.tag;
                    pintarControles();
                    aplicar();
                    document.getElementById('publicaciones').scrollIntoView({{ behavior: 'smooth' }});
                    return;
                }}
                var copiar = e.target.closest('.pub-copiar');
                if (copiar) {{
                    var cita = copiar.dataset.cita;
                    var listo = function () {{
                        var antes = copiar.innerHTML;
                        copiar.innerHTML = '<i class="fas fa-check"></i> Copiada';
                        setTimeout(function () {{ copiar.innerHTML = antes; }}, 1600);
                    }};
                    if (navigator.clipboard && navigator.clipboard.writeText) {{
                        navigator.clipboard.writeText(cita).then(listo, function () {{}});
                    }} else {{
                        var ta = document.createElement('textarea');
                        ta.value = cita; document.body.appendChild(ta); ta.select();
                        try {{ document.execCommand('copy'); listo(); }} catch (err) {{}}
                        document.body.removeChild(ta);
                    }}
                }}
            }});

            limpiar.addEventListener('click', function () {{
                Object.keys(estado).forEach(function (k) {{ if (k !== 'orden') estado[k] = ''; }});
                pintarControles();
                aplicar();
            }});

            // ---- exportar BibTeX de lo que esta a la vista --------------------
            function bibtexClave(it) {{
                var autor = (it.dataset.autores.split('|')[0] || 'licdia').split(',')[0];
                return autor.normalize('NFD').replace(/[^a-zA-Z]/g, '').toLowerCase() + it.dataset.anio;
            }}

            document.getElementById('pubBibtex').addEventListener('click', function () {{
                var visibles = items.filter(function (it) {{ return !it.hidden; }});
                if (!visibles.length) return;
                var usadas = {{}};
                var texto = visibles.map(function (it) {{
                    var clave = bibtexClave(it);
                    usadas[clave] = (usadas[clave] || 0) + 1;
                    if (usadas[clave] > 1) clave += String.fromCharCode(96 + usadas[clave]);
                    var titulo = it.querySelector('.pub-titulo').textContent.trim();
                    var autores = it.dataset.autores.split('|').join(' and ');
                    var venue = it.querySelector('.pub-venue').textContent.trim();
                    var enlace = it.querySelector('.pub-link');
                    var tipo = it.dataset.tipo === 'revista' ? 'article' :
                               (it.dataset.tipo === 'libro' ? 'book' : 'inproceedings');
                    var campo = it.dataset.tipo === 'revista' ? 'journal' : 'booktitle';
                    var l = ['@' + tipo + '{{' + clave + ',',
                             '  title   = {{' + titulo + '}},',
                             '  author  = {{' + autores + '}},',
                             '  year    = {{' + it.dataset.anio + '}},',
                             '  ' + campo + ' = {{' + venue + '}},'];
                    if (enlace) l.push('  url     = {{' + enlace.href + '}},');
                    l.push('}}');
                    return l.join('\\n');
                }}).join('\\n\\n');
                var blob = new Blob([texto], {{ type: 'application/x-bibtex;charset=utf-8' }});
                var a = document.createElement('a');
                a.href = URL.createObjectURL(blob);
                a.download = 'licdia-publicaciones.bib';
                document.body.appendChild(a); a.click(); document.body.removeChild(a);
                URL.revokeObjectURL(a.href);
            }});

            leerUrl();
            pintarControles();
            aplicar(false);
        }})();
    </script>
</body>

</html>
"""

dest = REPO / "publicaciones"
dest.mkdir(exist_ok=True)
(dest / "index.html").write_text(HTML, encoding="utf-8")
print(f"escrito: {dest / 'index.html'}")
print(
    f"publicaciones: {total} | autores: {len(autores)} | areas: {len(areas)} | sedes: {len(sedes)} | tags: {len(tags_todos)}"
)
print(f"con texto disponible: {n_acceso}")
print("areas:", ", ".join(f"{a} ({c})" for a, c in areas))
print("sedes:", ", ".join(f"{s} ({c})" for s, c in sedes))
