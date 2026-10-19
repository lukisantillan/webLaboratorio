#!/usr/bin/env python3
"""Arma el panel "Afinidad entre cursos" de la portada de la maestría: un dendrograma de los 8 cursos obligatorios.

Cada curso se representa por el embedding BGE-M3 de sus contenidos mínimos (Anexo III, Res. HCS 789/23), sin el
nombre del curso: cuatro nombres comparten "Ciencia de Datos" y eso los acercaba por el título y no por el contenido.
Agrupamiento jerárquico con distancia coseno y enlace promedio. El script verifica además que los primeros
agrupamientos se repitan con enlace completo y de Ward, y lo informa.

El bloque lleva la lista de fusiones (data-a, data-b, data-d, con la numeración de scipy: 0 a 7 los cursos, 8 en
adelante los grupos); js/mcd-afinidad.js dibuja el dendrograma a partir de ella.

Uso (necesita sentence-transformers y el modelo BAAI/bge-m3; el entorno de rag-unlu los tiene):
  python tools/maestria/afinidad.py                # calcula, guarda afinidad.json y renderiza
  python tools/maestria/afinidad.py --sin-calcular # renderiza con afinidad.json
"""

import argparse
import html
import json
import pathlib

AQUI = pathlib.Path(__file__).resolve().parent
PORTADA = AQUI.parents[1] / "maestria-ciencia-datos/index.html"
INICIO, FIN = "<!-- afinidad:inicio", "<!-- afinidad:fin -->"
CORTOS = ["Técnicas de análisis", "Fundamentos", "Aprendizaje automático", "Visualización",
          "Aplicada I", "Aplicada II", "Legales y éticos", "Taller de tesis"]
COMUNES = 5  # fusiones que se exige que coincidan entre enlaces para mencionarlo en la nota


def enumerar(nombres):
    return nombres[0] if len(nombres) == 1 else ", ".join(nombres[:-1]) + " y " + nombres[-1]


def calcular(cursos, modelo):
    from scipy.cluster.hierarchy import linkage
    from scipy.spatial.distance import pdist
    from sentence_transformers import SentenceTransformer

    E = SentenceTransformer(modelo, device="cpu").encode([c["contenidos_minimos"] for c in cursos], normalize_embeddings=True)

    def grupos(Z):
        conj, out = {i: frozenset([i]) for i in range(len(cursos))}, []
        for k, (a, b, _, _) in enumerate(Z):
            conj[len(cursos) + k] = conj[int(a)] | conj[int(b)]
            out.append(conj[len(cursos) + k])
        return out

    Z = linkage(pdist(E, "cosine"), "average")
    base = grupos(Z)[:COMUNES]
    coinciden = {met: set(grupos(linkage(E, "ward") if met == "ward" else linkage(pdist(E, "cosine"), met))[:COMUNES]) == set(base)
                 for met in ("complete", "ward")}
    return {"modelo": modelo, "Z": [[int(a), int(b), round(float(d), 4)] for a, b, d, _ in Z], "coinciden": coinciden}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sin-calcular", action="store_true")
    ap.add_argument("--modelo", default="BAAI/bge-m3")
    args = ap.parse_args()

    cursos = json.loads((AQUI / "contenidos_minimos.json").read_text(encoding="utf-8"))["obligatorios"]
    cache = AQUI / "afinidad.json"
    if args.sin_calcular:
        res = json.loads(cache.read_text(encoding="utf-8"))
    else:
        res = calcular(cursos, args.modelo)
        cache.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    n = len(cursos)
    miembros = {i: [i] for i in range(n)}
    fusiones = []
    for k, (a, b, d) in enumerate(res["Z"]):
        miembros[n + k] = miembros[a] + miembros[b]
        texto = " con ".join(enumerar([CORTOS[i] for i in miembros[x]]) for x in (a, b))
        d_txt = f"{d:.2f}".replace(".", ",")
        fusiones.append(f'                        <li data-a="{a}" data-b="{b}" data-d="{d}">Se agrupan {html.escape(texto)} '
                        f'(distancia {d_txt})</li>')
    cursos_li = "\n".join(f'                        <li data-c="{c["num"]}">{html.escape(CORTOS[i])}</li>' for i, c in enumerate(cursos))
    robusta = (" Los primeros cinco agrupamientos se repiten con enlace completo y de Ward."
               if all(res["coinciden"].values()) else "")
    bloque = f"""{INICIO} (generado por tools/maestria/afinidad.py; no editar a mano) -->
                <div class="mcd-afinidad mcd-panel-tablero" data-aos="fade-up">
                    <p class="mcd-recorrido-cab">Afinidad entre cursos <span>Contenidos mínimos · BGE-M3</span></p>
                    <ul class="mcd-afinidad-cursos" aria-label="Cursos obligatorios">
{cursos_li}
                    </ul>
                    <ol class="mcd-afinidad-fusiones" aria-label="Agrupamientos, del más cercano al más lejano">
{chr(10).join(fusiones)}
                    </ol>
                    <div class="mcd-afinidad-grafico" aria-hidden="true"></div>
                </div>
                <p class="mcd-recorrido-nota">Agrupamiento jerárquico de los contenidos mínimos de cada curso (Res. HCS 789/23):
                    embeddings BGE-M3, distancia coseno y enlace promedio.{robusta}</p>
                {FIN}"""
    s = PORTADA.read_text(encoding="utf-8")
    a, b = s.index(INICIO), s.index(FIN) + len(FIN)
    PORTADA.write_text(s[:a] + bloque + s[b:], encoding="utf-8")
    print("fusiones:", res["Z"], "| coinciden:", res["coinciden"])


if __name__ == "__main__":
    main()
