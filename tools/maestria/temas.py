#!/usr/bin/env python3
"""Arma el panel "Temas de la maestría" de la portada: un mapa de los temas de los contenidos mínimos.

Temas: cada oración de los contenidos mínimos de los 8 cursos obligatorios (Anexo III, Res. HCS 789/23). Si la
oración tiene la forma "Encabezado: a, b y c" o "Encabezado (a, b, c)", el encabezado y cada ítem son temas
aparte; el ítem se representa junto con su encabezado ("Votación — Métodos de combinación de modelos") para que
el embedding tenga contexto. Las demás oraciones quedan enteras.

Posición: t-SNE (perplejidad 12, semilla fija) sobre la distancia coseno entre embeddings BGE-M3. El script
informa qué fracción de los 5 vecinos más cercanos de cada tema se conserva en el plano.

El bloque lleva la lista de temas (data-x, data-y en [0, 1], data-c = curso); js/mcd-temas.js dibuja el mapa.

Uso (necesita sentence-transformers, scikit-learn y el modelo BAAI/bge-m3; el entorno de rag-unlu los tiene):
  python tools/maestria/temas.py                 # calcula, guarda temas.json y renderiza
  python tools/maestria/temas.py --sin-calcular  # renderiza con temas.json
  python tools/maestria/temas.py --listar        # solo muestra los temas extraídos
"""

import argparse
import html
import json
import pathlib
import re

AQUI = pathlib.Path(__file__).resolve().parent
PORTADA = AQUI.parents[1] / "maestria-ciencia-datos/index.html"
INICIO, FIN = "<!-- temas:inicio", "<!-- temas:fin -->"
CORTOS = ["Técnicas de análisis", "Fundamentos", "Aprendizaje automático", "Visualización",
          "Aplicada I", "Aplicada II", "Legales y éticos", "Taller de tesis"]
# Fórmulas del Taller que describen la asignatura y no son temas. Si después de la fórmula sigue una lista,
# cada ítem es un tema y el contexto indica de qué es parte.
FORMULAS = [(r"^La asignatura brinda conocimientos y apoyo para la ", None),
            (r"^Durante su desarrollo, las/los estudiantes deberán atender los criterios y pautas metodológicas en relación a:\s*",
             "pautas metodológicas de la tesis")]


def mayuscula(s):
    return s[:1].upper() + s[1:]


def items(lista):
    """'a, b y c' -> ['a', 'b y c']: se corta solo en comas; la última conjunción queda con su ítem."""
    return [x.strip() for x in lista.split(",") if x.strip()]


def extraer(cursos):
    temas = []
    for c in cursos:
        vistos = set()
        for oracion in re.split(r"\.\s+(?=[A-ZÁÉÍÓÚÑ(])", c["contenidos_minimos"].strip().rstrip(".")):
            oracion = oracion.strip().rstrip(".")
            partes = []
            for f, ctx in FORMULAS:
                if re.search(f, oracion):
                    oracion = re.sub(f, "", oracion)
                    if ctx and "," in oracion:
                        partes = [(x, ctx) for x in items(oracion)]
            m_par = re.match(r"^(.*?)\s*\(([^)]*,[^)]*)\)$", oracion)
            if partes:
                pass
            elif ":" in oracion:
                cab, cola = [x.strip() for x in oracion.split(":", 1)]
                if cab and ("," in cab or "," in cola or re.search(r"\s[ye]\s", cola)):
                    partes = [(x, None) for x in items(cab)] + [(x, cab) for x in items(cola)]
                elif not cab:
                    partes = [(x, None) for x in items(cola)]
            elif m_par:
                cab = m_par.group(1)
                partes = [(cab, None)] + [(x, cab) for x in items(m_par.group(2))]
            if not partes:
                partes = [(oracion, None)]
            for texto, contexto in partes:
                clave = texto.lower()
                if clave in vistos:  # "expresividad y efectividad" aparece dos veces en Visualización
                    continue
                vistos.add(clave)
                temas.append({"tema": mayuscula(texto), "contexto": contexto, "curso": c["num"]})
    return temas


def calcular(temas, modelo):
    import numpy as np
    from scipy.spatial.distance import pdist, squareform
    from sentence_transformers import SentenceTransformer
    from sklearn.manifold import TSNE

    textos = [t["tema"] + (f" — {t['contexto']}" if t["contexto"] else "") for t in temas]
    E = SentenceTransformer(modelo, device="cpu").encode(textos, normalize_embeddings=True)
    D = squareform(pdist(E, "cosine"))
    X = TSNE(n_components=2, metric="precomputed", init="random", perplexity=12, random_state=0, max_iter=4000).fit_transform(D)
    D2, k = squareform(pdist(X)), 5
    vecinos = float(np.mean([len(set(np.argsort(D[i])[1:k + 1]) & set(np.argsort(D2[i])[1:k + 1])) / k for i in range(len(temas))]))
    X = (X - X.min(0)) / (X.max(0) - X.min(0))
    return {"modelo": modelo, "vecinos_conservados": round(vecinos, 3),
            "temas": [dict(t, x=round(float(x), 4), y=round(float(y), 4)) for t, (x, y) in zip(temas, X)]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-calcular", action="store_true")
    ap.add_argument("--listar", action="store_true")
    ap.add_argument("--modelo", default="BAAI/bge-m3")
    args = ap.parse_args()

    cursos = json.loads((AQUI / "contenidos_minimos.json").read_text(encoding="utf-8"))["obligatorios"]
    if args.listar:
        for t in extraer(cursos):
            print(t["curso"], "|", t["tema"], f"  [{t['contexto']}]" if t["contexto"] else "")
        return
    cache = AQUI / "temas.json"
    if args.sin_calcular:
        res = json.loads(cache.read_text(encoding="utf-8"))
    else:
        res = calcular(extraer(cursos), args.modelo)
        cache.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    temas_li = "\n".join(
        f'                        <li data-c="{t["curso"]}" data-x="{t["x"]}" data-y="{t["y"]}" data-t="{html.escape(t["tema"])}"'
        f'{" data-ctx=" + chr(34) + html.escape(t["contexto"]) + chr(34) if t["contexto"] else ""}>{html.escape(t["tema"])}'
        f'{" (" + html.escape(t["contexto"]) + ")" if t["contexto"] else ""} · {html.escape(CORTOS[t["curso"] - 1])}</li>'
        for t in res["temas"])
    botones = "\n".join(f'                        <button type="button" data-c="{i + 1}" aria-pressed="false">{html.escape(c)}</button>'
                        for i, c in enumerate(CORTOS))
    bloque = f"""{INICIO} (generado por tools/maestria/temas.py; no editar a mano) -->
            <div class="mcd-temas" data-aos="fade-up">
                <p class="mcd-recorrido-cab">Temas de la maestría <span>{len(res["temas"])} temas · contenidos mínimos · BGE-M3</span></p>
                <div class="mcd-temas-filtro" role="group" aria-label="Resaltar los temas de un curso">
                    <button type="button" data-c="todos" aria-pressed="true">Todos</button>
{botones}
                </div>
                <ul class="mcd-temas-lista">
{temas_li}
                </ul>
                <div class="mcd-temas-grafico" aria-hidden="true"></div>
            </div>
            <p class="mcd-recorrido-nota">Cada punto es un tema de los contenidos mínimos de los ocho cursos obligatorios (Res. HCS 789/23).
                Posición: t-SNE sobre la distancia coseno entre embeddings BGE-M3; los temas cercanos tratan contenidos parecidos
                y los ejes no tienen unidades.</p>
            {FIN}"""
    s = PORTADA.read_text(encoding="utf-8")
    a, b = s.index(INICIO), s.index(FIN) + len(FIN)
    PORTADA.write_text(s[:a] + bloque + s[b:], encoding="utf-8")
    print(f"{len(res['temas'])} temas; vecinos conservados (k=5): {res['vecinos_conservados']}")


if __name__ == "__main__":
    main()
