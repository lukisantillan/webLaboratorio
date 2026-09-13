# Generador de /publicaciones/

La pagina `publicaciones/index.html` no se edita a mano: se genera desde estos scripts.

| Archivo | Que es |
|---|---|
| `gen_pubs_data.py` | **El dataset.** `PUBS` (una entrada por publicacion), `PROXIMAS` (trabajos a presentar), `LINKS` (DOI o repositorio, verificados) y `CITAS`. |
| `enriquecer.py` | Area, sede, idioma y palabras clave por publicacion. Se indexa por fragmento del titulo. |
| `render_pubs.py` | Arma el HTML con el panel de filtros, el JSON-LD y el export BibTeX. |
| `gen_banner.py` | Dibuja el banner del masthead a partir del conteo por ano (`SERIE`). |
| `barrido.py` | Cruza cada entrada contra OpenAlex, Crossref y Semantic Scholar: DOI, acceso abierto, citas. |
| `faltantes.py` | Inverso: que tiene OpenAlex bajo los autores del lab que no esta en el sitio. |

## Agregar una publicacion

1. Sumar un `dict(...)` a `PUBS` en `gen_pubs_data.py` (copiar uno existente).
2. Sumar su area / sede / idioma / keywords en `META` de `enriquecer.py` (si falta, `render_pubs.py` corta con un error que dice cual).
3. Si tiene DOI o deposito, sumarlo a `LINKS`. Solo enlaces comprobados.
4. `python3 tools/publicaciones/render_pubs.py`
5. Si cambio el conteo de algun ano, actualizar `SERIE` en `gen_banner.py` y correrlo (necesita Pillow).

Los barridos (`barrido.py`, `faltantes.py`) no tocan la pagina: escriben un JSON al lado y se lee a mano. Requieren red.
Esta carpeta esta excluida del deploy en `commands.sh`.
