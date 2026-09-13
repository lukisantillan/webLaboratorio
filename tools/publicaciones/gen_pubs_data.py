#!/usr/bin/env python3
"""Genera publicaciones/index.html para el sitio LICDIA UNLu."""

import html
import pathlib

REPO = pathlib.Path("/home/dp-note/code/teacher/diplomatura/site/webLaboratorio")

# tipo: congreso | revista | poster | libro
PUBS = [
    dict(
        anio=2026,
        fecha="Noviembre 2026",
        tipo="congreso",
        estado="Comunicación aceptada",
        titulo="Contabilidad Digital: propuesta y validación de un modelo metodológico para integrar automatización, analítica de datos e inteligencia artificial en PyMEs",
        autores="Meretta, F.; Fernández, J. M.",
        venue="VI Congreso Internacional de Investigación en Contabilidad y Empresa (CIICE 2026), Barcelona, España, 2 al 4 de noviembre",
    ),
    dict(
        anio=2026,
        fecha="Octubre 2026",
        tipo="congreso",
        estado="Aceptado para publicación",
        titulo="Remembering the Flow: Retrieval with Dynamic Turn Representations for Conversational Memory",
        autores="Fernández, J. M.; Errecalde, M.; Burdisso, S.",
        venue="XXXII Congreso Argentino de Ciencias de la Computación (CACIC 2026), Concepción del Uruguay, 5 al 9 de octubre",
    ),
    dict(
        anio=2026,
        fecha="Octubre 2026",
        tipo="congreso",
        estado="Aceptado para publicación",
        titulo="Un RAG portable sobre SUDOCU: consulta conversacional de normativa universitaria mediante estados de diálogo con procedencia",
        autores="Fernández, J. M.; Tamasi, F.; Marchetti, S.; Oloriz, M.; Errecalde, M.",
        venue="XXXII Congreso Argentino de Ciencias de la Computación (CACIC 2026), Concepción del Uruguay",
    ),
    dict(
        anio=2026,
        fecha="Octubre 2026",
        tipo="congreso",
        estado="Aceptado para publicación",
        titulo="Evidencia documental trazable con RAG: un asistente para auditorías GMP en la industria farmacéutica",
        autores="Pighin, M. E.; Fernández, J. M.",
        venue="XXXII Congreso Argentino de Ciencias de la Computación (CACIC 2026), Concepción del Uruguay",
    ),
    dict(
        anio=2026,
        fecha="Octubre 2026",
        tipo="congreso",
        estado="Aceptado para publicación",
        titulo="DM-AI: un director de juego multiagente basado en modelos de lenguaje para juegos de rol narrativos",
        autores="Baez, S.; Fernández, J. M.",
        venue="XXXII Congreso Argentino de Ciencias de la Computación (CACIC 2026), Concepción del Uruguay",
    ),
    dict(
        anio=2026,
        fecha="Agosto 2026",
        tipo="poster",
        estado="Segundo lugar — Poster Awards 2026",
        titulo="Parameter Efficiency or Efficient Full Fine-Tuning? PEFT vs. GaLore",
        autores="Camilo, M.; Fernández, J. M.; Errecalde, M.",
        venue="Second South American NLP School, Buenos Aires, 3 y 4 de agosto",
        pdf="../assets/poster-peft-vs-galore-nlp-school-2026.pdf",
    ),
    dict(
        anio=2026,
        fecha="Junio 2026",
        tipo="congreso",
        titulo="Performance vs. Efficiency in Domain-Specific LLM Adaptation: A Comparative Study of Full Fine-Tuning and LoRA on Real-World Data",
        autores="Camilo, M.; Fernández, J. M.; Errecalde, M.",
        venue="XIV Jornadas de Cloud Computing, Big Data &amp; Emerging Topics (JCC-BD&amp;ET 2026), La Plata",
    ),
    dict(
        anio=2026,
        fecha="Junio 2026",
        tipo="congreso",
        titulo="A Defense-in-Depth Architecture for Protecting AI Agent Intellectual Property in Multi-Tenant Cloud Environments",
        autores="Petrocelli, D.; Fernández, J. M.",
        venue="XIV Jornadas de Cloud Computing, Big Data &amp; Emerging Topics (JCC-BD&amp;ET 2026), La Plata",
    ),
    dict(
        anio=2025,
        fecha="2025",
        tipo="congreso",
        titulo="Agente basado en LLM para la ejecución de comandos CLI a partir de lenguaje natural: caso de estudio con Docker",
        autores="Robles, R.; Fernández, J. M.",
        venue="XXXI Congreso Argentino de Ciencias de la Computación (CACIC 2025)",
    ),
    dict(
        anio=2025,
        fecha="2025",
        tipo="congreso",
        titulo="Sistema de generación aumentada por recuperación (RAG) para el acceso a información académica",
        autores="Guerra, F.; Monti, K.; Fernández, J. M.",
        venue="XXXI Congreso Argentino de Ciencias de la Computación (CACIC 2025)",
    ),
    dict(
        anio=2025,
        fecha="Abril 2025",
        tipo="congreso",
        titulo="Fine-tuning y adaptación de modelos de lenguaje abiertos en infraestructura HPC para aplicaciones de dominio específico",
        autores="Fernández, J. M.; Petrocelli, D. M.; Matuk, R.; Lanson, D.; Zamudio, E.; Cagnina, L. C.; Errecalde, M. L.",
        venue="XXVII Workshop de Investigadores en Ciencias de la Computación (WICC 2025), Mendoza, 10 y 11 de abril",
    ),
    dict(
        anio=2024,
        fecha="2024",
        tipo="revista",
        titulo="Efectos de la incorporación de la bimodalidad en estudiantes que se declaran en situación de discapacidad en una universidad argentina",
        autores="Fernández, J. M.; Oloriz, M. G.",
        venue="Razón Crítica, (17), 1-18",
        nota="Estudio de las cohortes 2018 a 2022",
    ),
    dict(
        anio=2024,
        fecha="2024",
        tipo="libro",
        titulo="Computer Science — CACIC 2023 (libro de actas del XXIX Congreso Argentino de Ciencias de la Computación)",
        autores="Pesado, P.; Fernández, J. M.; Panessi, W. (eds.)",
        venue="Cham: Springer, 2024. ISBN 978-3-031-62245-8",
    ),
    dict(
        anio=2024,
        fecha="2024",
        tipo="revista",
        titulo="Sistemas de Información Ambiental como herramientas para la gestión pública de escala local: el caso del Sistema de Información Ambiental Integral (SIAI) del Partido de Luján, Provincia de Buenos Aires",
        autores="Lanson, D. E.; Iglesias, A. N.; Fernández, J. M.; Rosenfeld, A.",
        venue="Anuario de la División Geografía, (18), 1-10",
    ),
    dict(
        anio=2024,
        fecha="2024",
        tipo="revista",
        titulo="Productos y procesos de la extensión universitaria en el campo de la gestión ambiental. El Sistema de Información Ambiental Integrada (SIAI) del partido de Luján, Provincia de Buenos Aires",
        autores="Lanson, D.; Iglesias, A. N.; Fernández, J. M.",
        venue="Cuadernos de Extensión Universitaria de la UNLPam, Vol. 8, N.º 2, julio-diciembre 2024, Dossier. ISSN 2451-5930, e-ISSN 2718-7500",
    ),
    dict(
        anio=2023,
        fecha="2023",
        tipo="congreso",
        titulo="Instance retrieval from non-labeled data as a strategy for automatic classification of imbalanced e-mail datasets",
        autores="Fernández, J. M.; Errecalde, M. L.",
        venue="XXVIII Congreso Argentino de Ciencias de la Computación (CACIC 2022)",
    ),
    dict(
        anio=2023,
        fecha="Abril 2023",
        tipo="congreso",
        titulo="Descubrimiento de patrones de comportamiento vinculados al abandono en la Universidad Nacional de Luján mediante la aplicación de técnicas de aprendizaje automático",
        autores="Oloriz, M.; Fernández, J. M.; Jara, C.; Martínez, C.; Baquel, R.; Bertoglio, S.; Delfino, H.",
        venue="XXV Workshop de Investigadores en Ciencias de la Computación, Universidad Nacional del Noroeste, abril de 2023",
    ),
    dict(
        anio=2023,
        fecha="2023",
        tipo="congreso",
        titulo="Agrupamiento de Universidades Nacionales en función de sus características",
        autores="Martínez, C.; Delfino, H.; Bertoglio, S.; Oloriz, M.; Fernández, J. M.",
        venue="L Coloquio Argentino de Estadística 2023, Argentina",
    ),
    dict(
        anio=2023,
        fecha="2023",
        tipo="congreso",
        titulo="Herramientas de gestión ambiental sustentable y ordenamiento territorial del ámbito transicional ciudad-campo en gobiernos locales. El caso del Sistema de Información Ambiental Integrada del Municipio-Partido de Luján, Provincia de Buenos Aires, Argentina",
        autores="Iglesias, A. N.; Lanson, D.; Fernández, J. M.; Martínez, A.",
        venue="4th Polish-Colombian International Symposium",
    ),
    dict(
        anio=2022,
        fecha="2022",
        tipo="revista",
        titulo="La automatización de la certificación de títulos universitarios en Argentina como garantía del derecho al acceso a la información pública y la mejora en el uso de recursos",
        autores="Oloriz, M.; Rissi, M.; Fernández, J. M.; Masón, M. R.",
        venue="RAN — Revista Academia &amp; Negocios, 8(2)",
    ),
    dict(
        anio=2022,
        fecha="Junio 2022",
        tipo="congreso",
        titulo="Multi-class e-mail classification with a semi-supervised approach based on automatic feature selection and information retrieval",
        autores="Fernández, J. M.; Errecalde, M.",
        venue="Conference on Cloud Computing, Big Data &amp; Emerging Topics (pp. 75-90). Cham: Springer International Publishing",
    ),
    dict(
        anio=2022,
        fecha="Octubre 2022",
        tipo="congreso",
        titulo="Instance retrieval from non-labeled data as a strategy for automatic classification of imbalanced e-mail datasets",
        autores="Fernández, J. M.; Errecalde, M.",
        venue="EUDELAR 2022. ISBN 978-987-1364-31-2",
    ),
    dict(
        anio=2021,
        fecha="Abril 2021",
        tipo="congreso",
        titulo="Clasificación automática de correos electrónicos",
        autores="Fernández, J. M.; Cavasín, N.; Rodríguez, A.; Errecalde, M.",
        venue="XXIII Workshop de Investigadores en Ciencias de la Computación, Universidad Nacional de Chilecito, abril de 2021. ISBN 978-987-24611-3-3",
    ),
    dict(
        anio=2021,
        fecha="2021",
        tipo="congreso",
        titulo="Classic and recent (neural) approaches to automatic text classification: a comparative study with e-mails in the Spanish language",
        autores="Fernández, J. M.; Cavasin, N.; Errecalde, M.",
        venue="Short Papers of the 9th Conference on Cloud Computing, Big Data &amp; Emerging Topics (p. 20). Facultad de Informática (UNLP). ISBN 978-950-34-2016-4",
    ),
    dict(
        anio=2021,
        fecha="2021",
        tipo="congreso",
        titulo="Collaborative, distributed, scalable and low-cost platform based on microservices, containers, mobile devices and Cloud services to solve compute-intensive tasks",
        autores="Petrocelli, D.; De Giusti, A. E.; Naiouf, M.",
        venue="Euro-Par 2021 PhD Symposium (Parallel and Distributed Processing), Lisboa, Portugal",
    ),
    dict(
        anio=2020,
        fecha="2020",
        tipo="congreso",
        titulo="Plataforma colaborativa, elástica, de bajo costo y consumo basada en recursos de la Nube, contenedores y móviles para HPC",
        autores="Petrocelli, D.; De Giusti, A. E.; Naiouf, M.",
        venue="7.ª Conferencia Iberoamericana de Computação Aplicada, Lisboa, Portugal",
    ),
    dict(
        anio=2020,
        fecha="2020",
        tipo="congreso",
        titulo="Collaborative, distributed and scalable platform based on mobile, cloud, micro services and containers for intensive computing tasks",
        autores="Petrocelli, D.; De Giusti, A. E.; Naiouf, M.",
        venue="Short Papers of the 8th Conference on Cloud Computing, Big Data &amp; Emerging Topics (JCC-BD&amp;ET 2020)",
    ),
    dict(
        anio=2020,
        fecha="2020",
        tipo="revista",
        titulo="El rendimiento académico de los estudiantes en situación de discapacidad",
        autores="Oloriz, M.; Fernández, J. M.",
        venue="Revista RETOS XXI, 4(1)",
    ),
    dict(
        anio=2020,
        fecha="2020",
        tipo="congreso",
        titulo="Unconstrained Text Detection in Manga: a New Dataset and Baseline",
        autores="Del Gobbo, J.; Matuk Herrera, R.",
        venue="Advances in Image Manipulation (AIM) Workshop, ECCV 2020",
    ),
    dict(
        anio=2019,
        fecha="2019",
        tipo="congreso",
        titulo="Hybrid Elastic ARM&amp;Cloud HPC Collaborative Platform for Generic Tasks",
        autores="Petrocelli, D.; De Giusti, A. E.; Naiouf, M.",
        venue="VII Conference Cloud Computing &amp; Big Data, La Plata. ISBN 978-3-030-27713-0, pp. 16-27",
    ),
    dict(
        anio=2018,
        fecha="2018",
        tipo="congreso",
        titulo="A tool for modeling computational maps of the visual cortex in PyTorch (PyLissom)",
        autores="Barijhoff, H.; Matuk Herrera, R.",
        venue="Machine Learning Open Source Software Workshop, NIPS, Montreal, Canadá, 2018",
    ),
    dict(
        anio=2017,
        fecha="2017",
        tipo="congreso",
        titulo="Bioinspired self organizing neural networks for expression recognition",
        autores="Barijhoff, H.; Matuk Herrera, R.",
        venue="Women in Machine Learning Workshop, NIPS, Long Beach, EE. UU., 2017",
    ),
    dict(
        anio=2017,
        fecha="2017",
        tipo="congreso",
        titulo="Procesamiento distribuido y paralelo de bajo costo basado en Cloud &amp; móvil",
        autores="Petrocelli, D.; De Giusti, A. E.; Naiouf, M.",
        venue="CACIC 2017 — XXIII Congreso Argentino de Ciencias de la Computación, XVIII Workshop de Procesamiento Distribuido y Paralelo (WPDP), pp. 216-225",
    ),
]

# Trabajos enviados / a presentar: sede y fecha todavia sin confirmar.
PROXIMAS = [
    dict(
        tipo="congreso",
        titulo="Large Language Models actuales: arquitectura, limitaciones y perspectivas de evolución",
        autores="Fernández, J. M.; Oloriz, M.",
        eje="Tecnologías emergentes",
        resumen="Revisión narrativa de la evolución arquitectónica de los LLM y sus perspectivas de desarrollo, desde las redes recurrentes y los modelos secuencia a secuencia con atención hasta el Transformer y los modelos autorregresivos contemporáneos. Examina los aportes de la autoatención al modelado contextual y al escalamiento, las restricciones de memoria, contexto y costo computacional, y las limitaciones para generar información veraz. Explora modelos de espacio de estados selectivos, arquitecturas híbridas, Transformers de profundidad recurrente, memorias neuronales actualizables en inferencia y enfoques de predicción en espacios latentes como JEPA.",
        claves="modelos de lenguaje a gran escala; Transformers; modelos recurrentes; inteligencia artificial generativa; arquitecturas de IA",
    ),
    dict(
        tipo="congreso",
        titulo="Modelos fundacionales geoespaciales: arquitectura y perspectivas de adaptación para el análisis de propiedades del suelo",
        autores="Vazquez, J. M.; Fernández, J. M.",
        eje="IA en agricultura y sistemas agroalimentarios",
        resumen="Revisión técnica de los modelos fundacionales para observación de la Tierra y sus estrategias de adaptación, tomando como referencia Prithvi-EO-2.0 y TerraMind. Analiza objetivos de preentrenamiento, requisitos de entrada y alternativas de transferencia, con imágenes satelitales y perfiles edafológicos de fuentes públicas para estimar propiedades como pH, carbono orgánico y textura. Propone un esquema de evaluación que contempla la comparación con métodos convencionales, la validación espacial y los costos de adaptación.",
        claves="modelos fundacionales geoespaciales; observación de la Tierra; transferencia de aprendizaje; mapeo digital de suelos; adaptación de modelos",
    ),
]


# Enlaces verificados uno por uno (repositorio institucional, DOI o sitio de la revista).
# Clave: fragmento del titulo, comparado sin acentos ni mayusculas.
LINKS = {
    # DOI de capitulo/articulo cuando existe; si no, deposito en repositorio institucional.
    # Todos verificados con HTTP 200 (el de IADIS responde 406 a curl pero resuelve en navegador).
    "Unconstrained Text Detection in Manga": ("https://doi.org/10.1007/978-3-030-67070-2_38", "DOI"),
    "Hybrid Elastic ARM": ("https://doi.org/10.1007/978-3-030-27713-0_2", "DOI"),
    "Instance retrieval from non-labeled data": ("https://sedici.unlp.edu.ar/handle/10915/149456", "SEDICI", "CACIC"),
    "Clasificacion automatica de correos": ("https://doi.org/10.35537/10915/152375", "DOI"),
    "Fine-tuning y adaptacion de modelos": ("https://sedici.unlp.edu.ar/handle/10915/183892", "SEDICI"),
    "Agente basado en LLM para la ejecucion de comandos": ("https://sedici.unlp.edu.ar/handle/10915/191417", "SEDICI"),
    "Computer Science": ("https://link.springer.com/book/10.1007/978-3-031-62245-8", "Springer"),
    "Efectos de la incorporacion de la bimodalidad": ("https://doi.org/10.21789/25007807.2015", "DOI"),
    "La automatizacion de la certificacion": ("https://doi.org/10.29393/ran8-12acmm40012", "DOI"),
    "El rendimiento academico de los estudiantes": ("https://doi.org/10.33412/retosxxi.v4.1.2792", "DOI"),
    "Sistemas de Informacion Ambiental como herramientas": ("https://anuario-geografia.unlu.edu.ar/anugeografia/article/view/218", "Anuario"),
    "A tool for modeling computational maps": ("https://openreview.net/forum?id=rJex9Mc0Y7", "OpenReview"),
    "Collaborative, distributed, scalable and low-cost platform": ("https://doi.org/10.1007/978-3-031-06156-1_47", "DOI"),
    "Collaborative, distributed and scalable platform based on mobile": ("https://sedici.unlp.edu.ar/handle/10915/104766", "SEDICI"),
    "Plataforma colaborativa, elastica": ("https://doi.org/10.33965/ciawi_ciaca2020_202015l006", "DOI"),
    "Multi-class e-mail classification": ("https://doi.org/10.1007/978-3-031-14599-5_6", "DOI"),
    "Classic and recent (neural) approaches": ("https://sedici.unlp.edu.ar/handle/10915/125140", "SEDICI"),
}


# Citas recibidas segun OpenAlex / Crossref (se toma el mayor). Barrido del 13/09/2026.
CITAS = {
    "Unconstrained Text Detection in Manga": 10,
    "Multi-class e-mail classification": 2,
    "El rendimiento academico de los estudiantes": 2,
    "Collaborative, distributed, scalable and low-cost platform": 1,
    "Collaborative, distributed and scalable platform based on mobile": 1,
    "Hybrid Elastic ARM": 1,
}


def buscar_citas(titulo):
    import unicodedata

    def norm(x):
        return unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower()

    t = norm(titulo)
    for frag, n in CITAS.items():
        if norm(frag) in t:
            return n
    return 0


def buscar_link(titulo, venue=""):
    import unicodedata

    def norm(x):
        return unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower()

    t = norm(titulo)
    v = norm(venue)
    for frag, dato in LINKS.items():
        if norm(frag) not in t:
            continue
        # algunas entradas comparten titulo entre sedes distintas: exigir la sede
        if len(dato) == 3 and norm(dato[2]) not in v:
            continue
        return dato[0], dato[1]
    return None

