#!/usr/bin/env python3
"""Arma el bloque "La maestría en cuarenta términos" de la portada de la maestría.

Peso de cada término = TF × IDF, donde
  TF  = cantidad de cursos obligatorios en cuyos contenidos mínimos aparece (Anexo III, Res. HCS 789/23);
  IDF = log((1 + N) / (1 + df)) + 1, con df = documentos del digesto de la UNLu que lo contienen.
El digesto funciona como corpus de referencia: un término pesa más cuanto más cursos lo nombran y
menos lo usa el lenguaje normativo de la universidad.

Términos: palabras sueltas y segmentos cortos (2 a 4 palabras, 2 o 3 de contenido) delimitados por
la puntuación del propio texto o por "y"/"e"/"o", porque los contenidos mínimos son listas de temas.
Se quitan encabezados genéricos ("Introducción a la", "Conceptos básicos de"...).

El bloque lleva la lista de términos con su peso y su curso; js/mcd-terminos.js dibuja la nube.

Uso:
  python3 tools/maestria/terminos.py --digesto ../rag-unlu/indice/chunks.jsonl   # recalcula df y renderiza
  python3 tools/maestria/terminos.py                                             # renderiza con terminos.json
El df calculado queda en terminos.json, así el render no necesita el digesto.
"""

import argparse
import html
import json
import math
import pathlib
import re
import unicodedata
from collections import Counter, defaultdict

AQUI = pathlib.Path(__file__).resolve().parent
REPO = AQUI.parents[1]
PORTADA = REPO / "maestria-ciencia-datos/index.html"
CANTIDAD = 40
# Leyenda: 0 = término presente en más de un curso; 1 a 8 = cursos obligatorios en el orden del plan
CORTOS = ["Varios cursos", "Técnicas de análisis", "Fundamentos", "Aprendizaje automático", "Visualización",
          "Aplicada I", "Aplicada II", "Legales y éticos", "Taller de tesis"]
INICIO, FIN = "<!-- terminos:inicio", "<!-- terminos:fin -->"

VACIAS = set("""a al algo algunos ante antes aquel bajo cada como con contra cual cuales de del desde donde durante e el
ella ellos en entre era es esa ese eso esta estas este esto estos fue ha hacia hasta la las le les lo los mas mediante
menos mi muy nos o otra otro otros para pero por que se segun ser si sin sobre su sus tal tambien tanto todo todos un una
uno unos y ya""".split())
GENERICOS = [p.split() for p in sorted([
    "introduccion a la", "introduccion a", "conceptos basicos de", "nociones basicas de", "revision de",
    "conceptualizacion de", "conceptos sobre la", "conceptos sobre", "metodos para", "metodos de",
    "tecnicas de", "diseno de", "analisis de", "cuestiones de", "legislacion sobre la"], key=len, reverse=True)]
PAL = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+(?:-[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]+)*")
superficie = defaultdict(Counter)  # forma normalizada -> formas tal como aparecen en el texto


def normalizar(s):
    s = unicodedata.normalize("NFD", s.lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def terminos(texto, guardar=False):
    out = []
    for frase in re.split(r"[.,;:()\[\]“”\"–—]+|\s[yeo]\s", texto):
        orig = PAL.findall(frase)
        toks = [normalizar(t) for t in orig]
        for pref in GENERICOS:
            if toks[:len(pref)] == pref and len(toks) > len(pref):
                orig, toks = orig[len(pref):], toks[len(pref):]
                break
        for t, o in zip(toks, orig):
            if t not in VACIAS and len(t) >= 3 and not t.isdigit():
                if guardar:
                    superficie[t][o] += 1
                out.append(t)
        contenido = [t for t in toks if t not in VACIAS]
        if 2 <= len(contenido) <= 3 and len(toks) <= 4 and toks[0] not in VACIAS and toks[-1] not in VACIAS:
            clave = " ".join(toks)
            if guardar:
                superficie[clave][" ".join(orig)] += 1
            out.append(clave)
    return out


def calcular_df(digesto, candidatos):
    textos = defaultdict(list)
    with open(digesto, encoding="utf-8") as f:
        for linea in f:
            d = json.loads(linea)
            textos[d["documento"]].append(d.get("texto") or "")
    df = Counter()
    for partes in textos.values():
        df.update(set(terminos(" ".join(partes))) & candidatos)
    return len(textos), {t: df[t] for t in sorted(candidatos)}


def mostrar(clave):
    forma = superficie[clave].most_common(1)[0][0]
    return " ".join(w if (w.isupper() and len(w) > 1) else w.lower() for w in forma.split())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--digesto", help="chunks.jsonl del índice de rag-unlu; sin esto se usa el df guardado")
    args = ap.parse_args()

    datos = json.loads((AQUI / "contenidos_minimos.json").read_text(encoding="utf-8"))
    cursos = [set(terminos(c["contenidos_minimos"], guardar=True)) for c in datos["obligatorios"]]
    tf = Counter(t for c in cursos for t in c)
    cache = AQUI / "terminos.json"
    if args.digesto:
        n, df = calcular_df(args.digesto, set(tf))
    else:
        guardado = json.loads(cache.read_text(encoding="utf-8"))
        n, df = guardado["N"], guardado["df"]

    peso = {t: tf[t] * (math.log((1 + n) / (1 + df[t])) + 1) for t in tf}
    # Se recorren de mayor a menor peso (a igual peso, primero el más largo) y se descarta un término
    # contenido en otro ya elegido o que contiene a uno ya elegido: "verosimilitud" / "máxima verosimilitud".
    orden = sorted(peso, key=lambda t: (-peso[t], -len(t.split()), t))
    elegidos = []
    for t in orden:
        if any(re.search(rf"\b{re.escape(t)}\b", e) or re.search(rf"\b{re.escape(e)}\b", t) for e in elegidos):
            continue
        elegidos.append(t)
        if len(elegidos) == CANTIDAD:
            break
    elegidos.sort(key=lambda t: (-peso[t], mostrar(t)))

    cache.write_text(json.dumps({
        "N": n, "df": df,
        "elegidos": [{"termino": mostrar(t), "peso": round(peso[t], 3), "cursos": tf[t], "df": df[t]} for t in elegidos],
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    # Lista estática (lectores de pantalla, buscadores y respaldo sin JS). js/mcd-terminos.js la toma
    # de acá y dibuja la nube: tamaño lineal con el peso (data-p), color según el curso (data-c, 0 = varios).
    nombres = [c["nombre"] for c in datos["obligatorios"]]
    miles = f"{n:,}".replace(",", ".")
    hi, lo = peso[elegidos[0]], peso[elegidos[-1]]
    items = []
    for t in elegidos:
        p = (peso[t] - lo) / (hi - lo) if hi > lo else 1
        en = [i + 1 for i, c in enumerate(cursos) if t in c]
        c = en[0] if len(en) == 1 else 0
        tip = f"{' · '.join(nombres[i - 1] for i in en)} · {df[t]} de {miles} documentos del digesto"
        items.append(f'                        <li data-p="{p:.3f}" data-c="{c}" data-df="{df[t]}" '
                     f'data-cursos="{html.escape(" · ".join(nombres[i - 1] for i in en))}" '
                     f'title="{html.escape(tip)}">{html.escape(mostrar(t))}</li>')
    leyenda = "\n".join(f'                        <li data-c="{i}">{html.escape(corto)}</li>'
                        for i, corto in enumerate(CORTOS))
    bloque = f"""{INICIO} (generado por tools/maestria/terminos.py; no editar a mano) -->
                <div class="mcd-terminos" data-aos="fade-up">
                    <h3 class="mcd-terminos-titulo">La maestría en cuarenta términos</h3>
                    <div class="mcd-terminos-panel">
                        <ul class="mcd-terminos-lista" data-n="{miles}">
{chr(10).join(items)}
                        </ul>
                        <div class="mcd-terminos-nube" aria-hidden="true"></div>
                        <ul class="mcd-terminos-leyenda" aria-label="Color según el curso donde aparece el término">
{leyenda}
                        </ul>
                    </div>
                    <p class="mcd-terminos-nota">Tamaño según TF-IDF: cantidad de cursos obligatorios en cuyos contenidos mínimos
                        aparece el término (Res. HCS 789/23), ponderada por su rareza en los {miles} documentos del digesto de la UNLu.
                        Color según el curso donde aparece; en blanco, los que aparecen en más de uno.</p>
                </div>
                {FIN}"""

    s = PORTADA.read_text(encoding="utf-8")
    a, b = s.index(INICIO), s.index(FIN) + len(FIN)
    PORTADA.write_text(s[:a] + bloque + s[b:], encoding="utf-8")
    print(f"{len(elegidos)} términos; N = {n}")
    for t in elegidos:
        print(f"  {peso[t]:6.2f}  cursos={tf[t]}  df={df[t]:5d}  {mostrar(t)}")


if __name__ == "__main__":
    main()
