#!/usr/bin/env python3
"""Barrido inverso: que tiene OpenAlex bajo los autores del LICDIA que NO esta en el sitio.

Resuelve a cada autor por afiliacion (UNLu) para esquivar homonimos, baja todos sus
trabajos y los compara por titulo normalizado contra las 33 entradas cargadas.
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
SALIDA = pathlib.Path(__file__).parent / "faltantes.json"

# apellido a buscar -> nombre esperado (para descartar homonimos por parecido de nombre)
AUTORES = {
    "Fernández": "Juan Manuel Fernández",
    "Oloriz": "Mario Oloriz",
    "Petrocelli": "David Petrocelli",
    "Matuk Herrera": "Rosana Matuk Herrera",
    "Lanson": "Daniel Lanson",
}


def norm(s):
    s = (
        unicodedata.normalize("NFKD", s or "")
        .encode("ascii", "ignore")
        .decode()
        .lower()
    )
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def get(url):
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept": "application/json"}
    )
    for i in range(3):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except Exception as e:  # noqa: BLE001
            if i == 2:
                return {"_error": str(e)}
            time.sleep(2 * (i + 1))


# 1) institucion UNLu
inst = get(
    f"https://api.openalex.org/institutions?search=Universidad%20Nacional%20de%20Luj%C3%A1n&per-page=3&mailto={MAILTO}"
)
unlu = None
for i in inst.get("results", []):
    if "luj" in norm(i.get("display_name")):
        unlu = i
        break
if not unlu:
    raise SystemExit(f"no encontre UNLu en OpenAlex: {inst}")
unlu_id = unlu["id"].rsplit("/", 1)[-1]
print(
    f"UNLu en OpenAlex: {unlu['display_name']} ({unlu_id}), works={unlu.get('works_count')}"
)

# 2) autores: buscar por apellido y quedarse con los afiliados a UNLu (actual o historica)
autores = {}
for apellido, esperado in AUTORES.items():
    q = urllib.parse.quote(apellido)
    d = get(
        f"https://api.openalex.org/authors?search={q}&filter=affiliations.institution.id:{unlu_id}&per-page=10&mailto={MAILTO}"
    )
    cands = d.get("results", [])
    # elegir por parecido con el nombre esperado
    mejor = None
    for a in cands:
        r = difflib.SequenceMatcher(
            None, norm(a.get("display_name")), norm(esperado)
        ).ratio()
        if r >= 0.6 and (mejor is None or r > mejor[0]):
            mejor = (r, a)
    if mejor:
        a = mejor[1]
        autores[apellido] = a
        print(
            f"  {apellido:14s} -> {a['display_name']:28s} works={a.get('works_count'):3d} citas={a.get('cited_by_count'):4d} orcid={a.get('orcid')}"
        )
    else:
        print(
            f"  {apellido:14s} -> (sin match con afiliacion UNLu; candidatos: {[c.get('display_name') for c in cands][:4]})"
        )
    time.sleep(0.4)

# 3) trabajos de cada autor
vistos = {}
for apellido, a in autores.items():
    aid = a["id"].rsplit("/", 1)[-1]
    cursor = "*"
    while cursor:
        d = get(
            f"https://api.openalex.org/works?filter=authorships.author.id:{aid}&per-page=100&cursor={cursor}&mailto={MAILTO}"
        )
        for w in d.get("results", []):
            wid = w["id"]
            if wid in vistos:
                vistos[wid]["autores_licdia"].append(apellido)
                continue
            loc = w.get("primary_location") or {}
            vistos[wid] = {
                "titulo": w.get("display_name"),
                "anio": w.get("publication_year"),
                "doi": w.get("doi"),
                "tipo": w.get("type"),
                "fuente": (loc.get("source") or {}).get("display_name"),
                "landing": loc.get("landing_page_url"),
                "oa_url": (w.get("open_access") or {}).get("oa_url"),
                "citas": w.get("cited_by_count"),
                "autores": [
                    au.get("author", {}).get("display_name")
                    for au in w.get("authorships", [])
                ][:8],
                "instituciones": sorted({
                    i.get("display_name")
                    for au in w.get("authorships", [])
                    for i in (au.get("institutions") or [])
                    if i.get("display_name")
                }),
                "autores_licdia": [apellido],
            }
        cursor = (d.get("meta") or {}).get("next_cursor")
        time.sleep(0.4)

print(f"\ntrabajos distintos bajo esos autores en OpenAlex: {len(vistos)}")

# 4) diff contra el sitio
sitio = [norm(p["titulo"]) for p in PUBS]


def esta_en_sitio(titulo):
    t = norm(titulo)
    for s in sitio:
        if difflib.SequenceMatcher(None, t, s).ratio() >= 0.8:
            return True
    return False


def es_del_lab(w):
    unlu = any("luj" in norm(i) for i in w.get("instituciones", []))
    return unlu or len(set(w["autores_licdia"])) >= 2


todos = [w for w in vistos.values() if w["titulo"] and not esta_en_sitio(w["titulo"])]
faltan = [w for w in todos if es_del_lab(w)]
descartados = len(todos) - len(faltan)
print(f"descartados por no tener afiliacion UNLu ni 2 autores del lab (homonimos): {descartados}")
faltan.sort(key=lambda w: (-(w["anio"] or 0), w["titulo"]))
SALIDA.write_text(
    json.dumps(
        {"autores": {k: v.get("id") for k, v in autores.items()}, "faltan": faltan},
        ensure_ascii=False,
        indent=1,
    ),
    encoding="utf-8",
)

print(f"NO estan en el sitio: {len(faltan)}\n")
for w in faltan:
    print(f"- ({w['anio']}) {w['titulo'][:80]}")
    print(
        f"     {w['tipo']} | {w['fuente'] or '-'} | citas {w['citas']} | {w['doi'] or w['landing'] or '-'}"
    )
    print(f"     autores: {', '.join(a for a in w['autores'] if a)[:100]}")
print("\nescrito:", SALIDA)
