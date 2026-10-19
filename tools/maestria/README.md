# Herramientas de la Maestría en Ciencia de Datos

| Archivo | Que es |
|---|---|
| `contenidos_minimos.json` | **El dataset.** Contenidos minimos textuales del Anexo III de la Res. HCS 789/23: los 8 cursos obligatorios, las optativas (parrafo y 20 cursos previstos, con su carrera de origen) y los 3 cursos de nivelacion. Es la fuente del dorso de las tarjetas de la portada y del acordeon del plan de estudios. |
| `terminos.py` | Arma el bloque "La maestria en cuarenta terminos" de la portada, entre los marcadores `<!-- terminos:inicio -->` y `<!-- terminos:fin -->`: la lista de terminos con su peso (`data-p`), el curso (`data-c`, 0 = varios) y la leyenda. `js/mcd-terminos.js` dibuja la nube a partir de esa lista. |
| `terminos.json` | Salida de `terminos.py`: N y df de cada termino candidato en el digesto, y los 40 elegidos con su peso. Permite volver a renderizar sin el digesto. |
| `temas.py` | Arma el panel "Temas de la maestria" (entre `<!-- temas:inicio -->` y `<!-- temas:fin -->`): cada tema de los contenidos minimos de los 8 cursos obligatorios es un punto, ubicado por t-SNE sobre la distancia coseno entre embeddings BGE-M3. `js/mcd-temas.js` dibuja el mapa, con filtro por curso. |
| `temas.json` | Salida de `temas.py`: los temas con su posicion y la fraccion de vecinos conservados. Permite volver a renderizar sin el modelo. |
| `fotos/` | Fotos del equipo docente con fondo blanco y encuadre parejo. `recortar.swift` recorta el sujeto y detecta la cara con el framework Vision de macOS (como "Copiar sujeto" en Fotos); `componer.py` (Pillow) lo ubica sobre blanco en 480 x 480 con la cara al 32 % del alto (hasta 44 % si hay que agrandar para que el cuerpo llegue al borde) y funde los cortes de la foto original. Los originales quedan en `assets/img/mcd-docentes/_orig/`, fuera de git. |

## Fotos del equipo docente

    cd assets/img/mcd-docentes && mkdir -p /tmp/recorte
    swift ../../../tools/maestria/fotos/recortar.swift /tmp/recorte _orig/*.jpg
    python3 ../../../tools/maestria/fotos/componer.py /tmp/recorte .      # escribe <nombre>.jpg y <nombre>.webp

Para sumar o reemplazar a alguien, poner la foto original en `_orig/` con el nombre del archivo final. Rinden mejor
las fotos de medio cuerpo y de al menos 400 px; en las selfies muy cerradas el cuerpo no llega al borde y se funde.

## Metodo de `terminos.py`

Peso = TF x IDF. TF es la cantidad de cursos obligatorios en cuyos contenidos minimos aparece el termino;
IDF = log((1 + N) / (1 + df)) + 1, con df = documentos del digesto de la UNLu (indice de rag-unlu,
21.364 documentos normativos) que lo contienen. Los terminos son palabras sueltas y segmentos cortos
delimitados por la puntuacion del texto. En la nube, el tamano es lineal con el peso normalizado y el color
indica el curso donde aparece el termino (blanco si aparece en mas de uno).

## Uso

    python3 tools/maestria/terminos.py --digesto ../rag-unlu/indice/chunks.jsonl   # recalcula df (unos 20 s)
    python3 tools/maestria/terminos.py                                             # solo renderiza
    ../rag-unlu/.venv/bin/python tools/maestria/temas.py                            # recalcula (necesita sentence-transformers y BAAI/bge-m3)
    python3 tools/maestria/temas.py --sin-calcular                                 # solo renderiza

Esta carpeta no se despliega: en la VM solo van los archivos del sitio.
