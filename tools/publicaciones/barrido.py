#!/usr/bin/env python3
"""Barrido bibliografico de las 33 publicaciones contra OpenAlex, Crossref y Semantic Scholar.

Por cada entrada busca el DOI exacto, la URL de acceso abierto y la cantidad de citas.
Escribe barrido.json con un registro por publicacion y lo que se encontro en cada fuente.
"""

import difflib
import json
import pathlib
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gen_pubs_data import PUBS  # noqa: E402

MAILTO = "dmpetrocelli@gmail.com"
UA = f"licdia-pubs-sync/1.0 (mailto:{MAILTO})"
SALIDA = pathlib.Path(__file__).parent / "barrido.json"


def norm(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def get(url, reintentos=3):
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "application/json"}
    )
    for i in range(reintentos):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if i == reintentos - 1:
                return {"_error": str(e)}
            time.sleep(2 * (i + 1))


def parecido(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def mejor(candidatos, titulo, anio, clave_titulo, clave_anio):
    """Elige el candidato con titulo mas parecido; exige ratio alto y ano cercano."""
    top = None
    for c in candidatos:
        t = clave_titulo(c) or ""
        r = parecido(t, titulo)
        y = clave_anio(c)
        ok_anio = y is None or abs(int(y) - anio) <= 1
        if r >= 0.82 and ok_anio and (top is None or r > top[0]):
            top = (r, c)
    return top


def openalex(p):
    q = urllib.parse.quote(norm(p["titulo"])[:200])
    d = get(f"https://api.openalex.org/works?search={q}&per-page=5&mailto={MAILTO}")
    m = mejor(
        d.get("results", []),
        p["titulo"],
        p["anio"],
        lambda w: w.get("display_name"),
        lambda w: w.get("publication_year"),
    )
    if not m:
        return None
    r, w = m
    oa = w.get("open_access") or {}
    loc = w.get("primary_location") or {}
    return {
        "ratio": round(r, 3),
        "id": w.get("id"),
        "doi": w.get("doi"),
        "citas": w.get("cited_by_count"),
        "oa_url": oa.get("oa_url"),
        "landing": loc.get("landing_page_url"),
        "fuente": (loc.get("source") or {}).get("display_name"),
        "anio": w.get("publication_year"),
    }


def crossref(p):
    q = urllib.parse.quote(p["titulo"][:200])
    d = get(
        f"https://api.crossref.org/works?query.bibliographic={q}&rows=5&mailto={MAILTO}"
    )
    items = (d.get("message") or {}).get("items", [])
    m = mejor(
        items,
        p["titulo"],
        p["anio"],
        lambda w: (w.get("title") or [""])[0],
        lambda w: ((w.get("issued") or {}).get("date-parts") or [[None]])[0][0],
    )
    if not m:
        return None
    r, w = m
    return {
        "ratio": round(r, 3),
        "doi": w.get("DOI"),
        "url": w.get("URL"),
        "contenedor": (w.get("container-title") or [None])[0],
        "citas": w.get("is-referenced-by-count"),
    }


def semantic(p):
    q = urllib.parse.quote(p["titulo"][:200])
    d = get(
        "https://api.semanticscholar.org/graph/v1/paper/search"
        f"?query={q}&limit=5&fields=title,year,citationCount,externalIds,openAccessPdf,url"
    )
    m = mejor(
        d.get("data", []),
        p["titulo"],
        p["anio"],
        lambda w: w.get("title"),
        lambda w: w.get("year"),
    )
    if not m:
        return None
    r, w = m
    return {
        "ratio": round(r, 3),
        "doi": (w.get("externalIds") or {}).get("DOI"),
        "citas": w.get("citationCount"),
        "pdf": (w.get("openAccessPdf") or {}).get("url"),
        "url": w.get("url"),
    }


resultados = []
for i, p in enumerate(PUBS, 1):
    reg = {"titulo": p["titulo"], "anio": p["anio"], "tipo": p["tipo"]}
    reg["openalex"] = openalex(p)
    reg["crossref"] = crossref(p)
    reg["semantic"] = semantic(p)
    # S2 limita a ~100 req / 5 min sin clave: ir despacio
    time.sleep(1.2)
    resultados.append(reg)
    hallado = [k for k in ("openalex", "crossref", "semantic") if reg[k]]
    print(
        f"[{i:02d}/{len(PUBS)}] {p['titulo'][:55]:<55} -> {', '.join(hallado) or 'nada'}"
    )

SALIDA.write_text(
    json.dumps(resultados, ensure_ascii=False, indent=1), encoding="utf-8"
)
print("escrito:", SALIDA)
