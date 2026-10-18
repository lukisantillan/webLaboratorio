# Changelog

All notable changes to the LICDIA UNLu website are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Versioning policy for this project:

- **MAJOR**: structural site reorganization, breaking URL changes, or major redesign
- **MINOR**: new pages, new features (forms, integrations), new sections
- **PATCH**: bug fixes, content updates, performance and SEO tweaks, asset additions

## [Unreleased]

### Added
- Maestría: Mg. Diego Gasch se suma al cuerpo docente (ciencia de datos y aprendizaje automático aplicado, UNLu), con foto en `assets/img/mcd-docentes/diego-gasch.{jpg,webp}`.
- Maestría: tres fotos ilustrativas de Unsplash (Unsplash License; Vitaly Gariev, Carlos Muza y Luke Chesser) en `assets/img/mcd-fotos/`, ubicadas en Información, ¿Por qué elegirnos? y Salida académica y profesional, con un zoom lento que se desactiva con `prefers-reduced-motion`. Logos oficiales de UADER y CONEAU en la banda de Acreditación, tomados de uader.edu.ar y coneau.gob.ar.
- Maestría: perfil de Mario Oloriz (`maestria-ciencia-datos/docentes/oloriz/`), responsable propuesto de Aspectos Legales y Éticos, con su foto de la sección Equipo. Entrada en `sitemap.xml`.
- Maestría: tarjetas de cursos optativos (2 × 48 hs, Optativa I: IA Generativa) y de cursos de nivelación (Cherencio, Jara, Croch) en el plan de estudios; etiqueta "En trámite" (`.tag-tramite`, inline en cada página) para estado, fechas y aranceles de la primera cohorte.
- Home: noticia del segundo lugar en los Poster Awards 2026 de la Second South American NLP School (Camilo, Fernández, Errecalde, "PEFT vs. GaLore"), con el póster en `assets/img/noticias/` y el PDF en `assets/`.
- Home: 8 entradas 2026 en la timeline de publicaciones (CIICE 2026, 4× CACIC 2026, póster NLP School, 2× JCC-BD&ET 2026).
- Home: Mario Oloriz y Hugo Delfino vuelven a la sección Equipo (UNLu), con sus fotos y descripciones previas a la baja de mayo de 2026. Las 15 fichas UNLu quedan en filas completas de a tres.
- Home: Franco Chappe se suma a la sección Equipo (UNLu) como estudiante de la Lic. en Sistemas de Información y ayudante de la División Computación, con foto en `assets/img/team/chappe.{jpg,webp}`.
- Publicaciones: entrada del WICC 2024 (Fernández, Lanson, Iglesias, Cagnina, Errecalde, "Generación de herramientas de explotación de información ambiental desde bases de datos textuales a partir de técnicas de inteligencia artificial"), que estaba en el CV del director y faltaba en el sitio. El banner pasa a contar 5 publicaciones en 2024.
- Publicaciones: texto completo en PDF (versión de autor) para seis trabajos, en `publicaciones/pdf/`: los cuatro de CACIC 2026, el de JCC-BD&ET 2026 de Petrocelli y Fernández, y el de WICC 2023 sobre abandono en la UNLu. Se suman enlaces verificados para tres trabajos más: SEDICI para el de CACIC 2025 de Guerra, Monti y Fernández y para el de WICC 2024, y DOI para el artículo de Cuadernos de Extensión UNLPam 2024. El botón dice "Texto completo (PDF)", salvo en los pósters.
- Home: enlace al texto completo en las entradas de la línea de tiempo que lo tienen, como píldora (`.timeline-pdf` en `css/styles.css`) debajo de la cita: PDF, SEDICI o Póster.

### Changed
- Maestría, revisión integral del texto con el registro de los micrositios de posgrado de Stanford y CMU y de las fichas de universidades nacionales: títulos cortos y nominales, bajadas con un dato concreto, voz impersonal, sin relleno ("fundamentos teóricos sólidos", "demanda creciente", "respaldo normativo completo") ni anglicismos ("Data Scientist", "machine learning", "pipelines", "dashboards", "clustering"), "h" en lugar de "hs", sin signos "+" ni rayas en el texto. El encabezado de la portada nombra a las dos universidades y muestra "Primera cohorte 2027 · apertura en trámite"; las subpáginas llevan el nombre del programa como antetítulo y pierden el título repetido debajo del encabezado. Se quitan la comparación de precios con posgrados privados, la afirmación de "única maestría pública del corredor" y las referencias a responsables de curso. Se corrige "Ciencias de Datos" en el nombre del primer curso y la frase de la portada que remitía a los docentes del plan de estudios.
- Maestría: la modalidad se presenta como cursada sincrónica, "en forma remota o en el aula", en la portada (ficha, fila de datos, franja con "sin necesidad de viajar", Modalidad, resumen del plan), plan de estudios, enfoque, por qué elegirnos y requisitos. "Presencial" queda solo como dato de acreditación en la pregunta frecuente sobre modalidad ("en el marco de la modalidad presencial con la que la carrera está acreditada"). En los datos estructurados, `courseMode` pasa de `onsite` a `blended`.
- Maestría, Fortalezas: "Accesible y pública" y "Cursos individuales" se reemplazan por "Cursada sincrónica y remota" y "Vínculo con la investigación" (articulación con el LICDIA).
- Maestría: el horario se enuncia como dato, al modo de las fichas de otras universidades: "Dos veces por semana, de 18 a 21 h" en la ficha, la franja y la etiqueta de Modalidad. El subtítulo de Modalidad deja de repetir la compatibilidad con el trabajo, que ya dice la franja.
- Maestría: la sección "Cuerpo docente" pasa a "Equipo docente" (título y menú). La nota de la grilla dice "La asignación de docentes a cada curso puede modificarse" en lugar de la referencia al plantel validado y a los responsables por confirmar.
- Maestría: Presentación queda en un solo párrafo (carrera de posgrado UNLu y FCyT-UADER, acreditada por CONEAU, con título de validez nacional, y qué forma). Salen el detalle normativo, que está en Acreditación, la justificación de demanda, la afirmación sobre el corredor conurbano-litoral y el rótulo Objetivos; quedan las tarjetas Analizar, Modelar y Comunicar.
- Maestría: el desenfoque pasa de la foto de la franja a la de Presentación, que lleva además un velo bordó para quitarle detalle; la franja vuelve a su foto nítida.
- Maestría: el horario se presenta como pensado para quienes trabajan. La franja con foto dice "Diseñada para profesionales que trabajan a tiempo completo", la ficha suma el rótulo "Horario" y el subtítulo de Modalidad menciona la compatibilidad con un trabajo de tiempo completo. En todo el subsitio, "a partir de las 18 hs" pasa a "desde las 18 h" y "presenciales y/o virtuales" a "presenciales o virtuales". La foto de la franja va desenfocada para quitarle protagonismo.
- Maestría: sin íconos decorativos ni emojis. Las cifras y los números de curso pasan a serif, las tarjetas llevan un filete bordó sobre el título y la línea de tiempo usa puntos simples. Se mantienen los íconos funcionales: menú, WhatsApp, flechas de navegación, copiar datos bancarios, enlaces de los perfiles docentes y avisos.
- Maestría: la foto de Presentación es ahora una clase del Congreso Argentino de Estadística, del archivo de LICDIA, en lugar de la foto de Unsplash. En aranceles, "¿Necesitás factura?" pasa a "Facturación".
- Maestría, las 21 páginas: tipografía Source Serif 4 para títulos grandes (encabezado, títulos de sección y franjas) y Source Sans 3 para el resto, en reemplazo de Poppins, Montserrat, Roboto Slab y DM Mono, con los micrositios de posgrado de Stanford y CMU como referencia. Encabezado más bajo, menú en una línea sin mayúsculas e ítem activo en bordó. Los estilos están en `css/mcd-visual.css`, que ahora enlazan todas las páginas del subsitio.
- Maestría: registro sobrio e impersonal, con encabezados nominales y llamados en infinitivo ("Solicitar información", "Primera cohorte 2027", "Fortalezas del programa", "Presentación", "Cursada vespertina", "Solicitud de información", "Enviar solicitud"). El menú dice "Fortalezas" y "Contacto". Las tarjetas de Modalidad pasan a "Régimen de cursada", "Carga horaria" y "Tesis de maestría". Se reescriben sin voseo los cierres de los perfiles docentes y los textos de destinatarios, aranceles, requisitos e inscripción, y las descripciones para redes dejan de empezar con "Conocé". Las páginas de agradecimiento conservan su tono.
- Maestría: el horario de los encuentros figura como "a partir de las 18 hs" en la portada del subsitio (ficha, banda "Así se cursa", Modalidad con etiqueta propia, FAQ y schema), en plan de estudios, enfoque y por qué elegirnos.
- Maestría (portada del subsitio): rediseño visual sin cambios de contenido, con estilos en `css/mcd-visual.css`, que solo cargan las páginas de la Maestría. Franja de cifras (776 hs, 10 cursos, 2 universidades, 50% de beca UNLu, 2 años); el plan de estudios pasa de acordeón a tarjetas en dos columnas con ícono, número, horas y el mismo texto de cada curso; banda con foto (`curso-rosana`) y velo bordó entre Plan de estudios y Cuerpo docente; Modalidad de cursada sobre `fondo-cursos` con velo oscuro; Cuerpo docente en tres columnas con fotos de 176 px y versión webp; banda de logos en Acreditación (escudo de la UNLu en `assets/img/mcd-logos/`, UADER y CONEAU con su nombre en texto).
- Maestría: la línea de calendario de Modalidad pasa a una línea de tiempo de cinco hitos (Inscripción, Nivelación, Primer año, Segundo año, Tesis) con la etiqueta "En trámite"; la misma línea de tiempo se suma arriba de la tabla del cronograma en `plan-de-estudios/`.
- Maestría: primera cohorte pasa de "segundo semestre 2026" a 2027 con apertura en trámite, en home del subsitio, plan de estudios, requisitos, inscripción, por qué elegirnos, destinatarios, enfoque y aranceles (texto, FAQ, schema FAQPage y Course). Calendario proyectado: inscripción 16/11/2026 a 1/4/2027 con admisión continua, nivelación 12/4 a 7/5/2027, cursada del 17/5/2027 al 27/10/2028, tesis desde noviembre de 2028.
- Maestría: modalidad de cursada pasa de "2 clases de 4 hs, 75% presencial" a dos encuentros semanales sincrónicos de 3 hs, presenciales y/o virtuales (60% de la carga horaria), en bloques de 6 semanas (8 para Aprendizaje Automático).
- Maestría: aranceles pasan a matrícula de $400.000, 16 cuotas mensuales de $400.000 en los meses con cursada, derecho de nivelación de $400.000 (solo quienes nivelan) y derecho de defensa de $400.000; total $7.200.000 ($3.600.000 con beca UNLu); revisión semestral por IPC; cursos individuales a 1,5 cuotas por curso.
- Maestría: responsables propuestos para la primera cohorte: Técnicas de Análisis y Visualización a confirmar (FCyT-UADER), Aprendizaje Automático Rosana Matuk, Aspectos Legales Mario Oloriz; el subtítulo de Cuerpo docente ya no afirma que los responsables son los validados por CONEAU. "Comisión Académica" pasa a "Comité Académico".
- Home: el enlace "Maestría en Ciencia de Datos" apunta al subsitio `maestria-ciencia-datos/` en lugar de la página de la UNLu.
- `sitemap.xml`: lastmod 2026-10-17 en las páginas modificadas de la Maestría.
- Home: las fotos del carrusel pasan de 4032 px de ancho a 1600 px (webp de 0,7–1,4 MB a 0,12–0,20 MB).
- Home: las bajadas de sección y el subtítulo del hero pasan de Roboto Slab itálica a Montserrat, con ancho máximo para las bajadas y sombra en el subtítulo. "Más información" y el ítem activo del menú pasan del violeta al azul de la línea de tiempo (#1d13b9). Los estilos están acotados a la home (`body.home`).
- Home: la línea de tiempo muestra solo 2025 y 2026. Las anteriores siguen en Publicaciones, a la que lleva el botón "Ver todas las publicaciones".
- Home y Publicaciones: "Remembering the Flow" (Fernández, Errecalde, Burdisso) figura como trabajo distinguido del Workshop de Bases de Datos y Minería de Datos de CACIC 2026. En Publicaciones el cambio va en `tools/publicaciones/gen_pubs_data.py` y la página se regeneró.

### Fixed
- Maestría: títulos de Enrique Álvarez (Dr., figuraba como Lic.) y Santiago Banchero (Mg., figuraba como Lic.) en la grilla de docentes y en sus perfiles.
- Maestría: el botón flotante "Solicitar información" tenía texto bordó sobre fondo bordó en móvil, porque la regla general de enlaces de `mcd-style2.css` (bordó con `!important`) le ganaba a su color blanco.
- Aranceles: quedaba un emoji, escrito como entidad HTML, en el título "Cómo pagar".
- Maestría: los íconos de Font Awesome en SVG de las tarjetas quedaban oscuros sobre el círculo bordó al pasar el mouse; ahora son bordó en reposo y blancos en hover.
- Home: el póster de la NLP School cargaba en diferido sin alto reservado (pasaba de 0 a 791 px) y corría 767 px todo lo que estaba debajo, de modo que los enlaces del menú a Cursos, Equipo y Contacto terminaban en la sección anterior. La imagen declara ahora `width` y `height`.
- Home: la tarjeta del curso de posgrado de UNTREF (2024) mostraba una imagen rota, porque la tomaba del sitio de UNTREF y ese archivo ya no existe. Ahora usa una placa propia, `assets/img/curso-untref-2024.{jpg,webp}`.
- Home: grilla de Líneas de I+D sin el hueco de la segunda fila (se quitó una columna vacía y la fila se centra). En Proyectos, la última tarjeta usa una clase válida (`col-lg-15` pasa a `col-lg-4`) y queda centrada.
- Home: al entrar desde el menú, la barra fija ya no tapa el título de la sección (`scroll-margin-top`).
- Home: la sección de Clementina XXI repetía `id="portfolio"`. Pasa a `id="clementina"`.
- Home: el enlace "Ver mapa ampliado" en Contacto ahora se lee sobre el fondo oscuro.
- Publicaciones: se quita la entrada duplicada de "Instance retrieval from non-labeled data…" (EUDELAR 2022). Es el mismo trabajo que la entrada de CACIC, que ya enlaza a SEDICI. El banner pasa a contar 2 publicaciones en 2022.
- Home: lista de autores completa en la entrada WICC 2025 (faltaban Zamudio y Cagnina).

### Removed
- Maestría: los nombres de docentes asignados a cada curso, fuera de la grilla de Equipo docente. Sale "a cargo de Fernando Bordignon" de la tarjeta de Tesis en la portada y de por qué elegirnos; en el plan de estudios sale el "Docente Responsable" de cada curso y los cursos de nivelación indican áreas en lugar de nombres. Se conservan la carga horaria y la institución que dicta cada curso.
- Maestría: los once perfiles individuales de docentes, que no tenían el aval de cada docente y contenían datos desactualizados. Cada URL queda como una página que redirige a la grilla de Cuerpo docente con `noindex`, y salen del `sitemap.xml`. La grilla conserva nombre, título, área e institución, sin el enlace "Ver perfil".
- Maestría, aranceles: Pago Mis Cuentas (pago electrónico y por cajero), que la UNLu dejó de usar. El pago queda por transferencia bancaria.
- Maestría: la mención al 40% de trabajo guiado (portada, FAQ y schema, plan de estudios, enfoque y por qué elegirnos).
- Plan de estudios: bloque "¿Por qué este cronograma?".
- Home: script del kit de Font Awesome (`kit.fontawesome.com/eb496ab1a0.js`), que respondía 403 y era redundante con `use.fontawesome.com` v6.3.0 y el CSS de cdnjs ya cargados.

## [1.0.0] - 2026-06-03

First tagged release. Marks the site as stable after the multi-PR overhaul completed during May–June 2026 (PRs #1–#13 plus this cleanup batch).

### Added
- 70 missing WebP renditions across `assets/img/` (team, mcd-docentes, ipc-fotos, investigaciones, og-*). Site-wide WebP coverage now at 146 files.
- `assets/img/og-default.jpg` and `og-default.webp` (1200×630) for Open Graph fallback used by home and `/charla/*` pages.
- `<h1>` heading on home `masthead-heading` for proper SEO hierarchy.
- Populated `<meta name="description">` on home (was empty).
- `.gitignore` rule for browser "Save Page As Complete" dumps (`**/*_files/`).
- This `CHANGELOG.md`.

### Changed
- WhatsApp deep-link query strings now URL-encode non-ASCII characters (`información` → `informaci%C3%B3n`, `Maestría` → `Maestr%C3%ADa`, `ñ` → `%C3%B1`). WhatsApp was returning HTTP 400 on the previous unencoded links across 46 HTML files.
- `<html lang="en">` corrected to `<html lang="es">` on 15 Spanish-language pages (home, política de privacidad, inscripción dev-ia, proyecto-enseñanza/*, director/*, logos, LLM, fitba-13c, ipc).

### Removed
- Google Maps JS embed (`maps.googleapis.com/maps/api/js`) replaced by a static OpenStreetMap iframe centered on UNLu Luján (−34.5689, −59.1044). Removes the dependency on an exposed and now-revoked Google API key in 5 HTML files (home, política de privacidad, proyecto-enseñanza/{index, juego, ia}).

### Fixed
- Broken images: `assets/img/team/{2,3,4,5,6}.webp` (referenced from `<picture>` but missing on filesystem) and similar gaps across `mcd-docentes/`, `ipc-fotos/`, `investigaciones/`.
- Broken `og:image` on home and `/charla/*` (`og-default.jpg` was referenced but did not exist).

### Security
- Removed the publicly exposed Google Maps API key (`AIzaSy…IE4o`) from all HTML sources. The key should be rotated/revoked in Google Cloud Console if not already.

## Pre-1.0.0 history

Prior history is tracked in the merged PRs:

- **#13** — Parallel agent batch: performance (WebP + minified JS), SEO (OG meta in 23 pages, noindex propuestas, sitemap lastmod), security (Turnstile placeholder, honeypot, ZIP fallback), 404 page, blog index and RSS feed.
- **#12** — `LICDIAForm` shared module with size validation, upload progress, 120 s timeout, ZIP fallback for WhatsApp.
- **#11** — Migrated form webhook to a named Cloudflare tunnel at `n8n.impulsate.lat` (URL no longer rotates on pod restart).
- **#10** — Hotfix for rotating `cloudflared` quick-tunnel URL.
- **#9** — `Aprox.` prefix in date chips; BC timeline uses purple brand palette instead of IA blue.
- **#8** — Horizontal "Proceso de inscripción" timeline with 4 steps and tentative dates on both diplomatura homes.
- **#7** — All Blockchain inscription CTAs point to `/charla/blockchain/#inscripcion`.
- **#6** — 2025 IA Generativa informative talk added as YouTube embed (matches Blockchain layout).
- **#5** — Dark mode, microinteractions, English-language blog SEO.
- **#1–#4** — Initial cohort and content updates.

[Unreleased]: https://github.com/lukisantillan/webLaboratorio/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/lukisantillan/webLaboratorio/releases/tag/v1.0.0
