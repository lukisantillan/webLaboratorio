#!/usr/bin/env python3
"""Metadatos extra por publicacion: area, sede normalizada, idioma y palabras clave.

Se indexa por un fragmento del titulo (comparado sin acentos ni mayusculas) para no
duplicar el dataset que ya vive en gen_pubs.py.
"""

# area | idioma | sede corta | palabras clave
META = {
    "Contabilidad Digital": (
        "IA aplicada",
        "es",
        "CIICE",
        ["automatización", "analítica de datos", "PyMEs", "contabilidad"],
    ),
    "Remembering the Flow": (
        "LLM y PLN",
        "en",
        "CACIC",
        ["memoria conversacional", "recuperación de información", "diálogo"],
    ),
    "Un RAG portable sobre SUDOCU": (
        "LLM y PLN",
        "es",
        "CACIC",
        ["RAG", "normativa universitaria", "estados de diálogo", "procedencia"],
    ),
    "Evidencia documental trazable": (
        "LLM y PLN",
        "es",
        "CACIC",
        ["RAG", "auditoría", "industria farmacéutica", "trazabilidad", "GMP"],
    ),
    "DM-AI": (
        "LLM y PLN",
        "es",
        "CACIC",
        ["sistemas multiagente", "generación narrativa", "juegos de rol"],
    ),
    "Parameter Efficiency or Efficient Full Fine-Tuning": (
        "LLM y PLN",
        "en",
        "NLP School",
        ["PEFT", "GaLore", "fine-tuning", "eficiencia", "LLaMA"],
    ),
    "Performance vs. Efficiency in Domain-Specific": (
        "LLM y PLN",
        "en",
        "JCC-BD&ET",
        ["fine-tuning", "LoRA", "adaptación de dominio"],
    ),
    "A Defense-in-Depth Architecture": (
        "Seguridad",
        "en",
        "JCC-BD&ET",
        ["agentes de IA", "propiedad intelectual", "multi-tenant", "cloud"],
    ),
    "Agente basado en LLM para la ejecución de comandos": (
        "LLM y PLN",
        "es",
        "CACIC",
        ["agentes", "CLI", "Docker", "lenguaje natural"],
    ),
    "Sistema de generación aumentada por recuperación": (
        "LLM y PLN",
        "es",
        "CACIC",
        ["RAG", "información académica", "recuperación de información"],
    ),
    "Fine-tuning y adaptación de modelos de lenguaje": (
        "LLM y PLN",
        "es",
        "WICC",
        ["fine-tuning", "HPC", "dominio específico", "modelos abiertos"],
    ),
    "Efectos de la incorporación de la bimodalidad": (
        "Educación superior",
        "es",
        "Razón Crítica",
        ["bimodalidad", "discapacidad", "inclusión", "cohortes"],
    ),
    "Computer Science": (
        "Edición científica",
        "en",
        "CACIC",
        ["actas", "edición", "congreso"],
    ),
    "Sistemas de Información Ambiental como herramientas": (
        "Ambiente y territorio",
        "es",
        "Anuario División Geografía",
        ["SIAI", "gestión pública", "información ambiental", "escala local"],
    ),
    "Productos y procesos de la extensión universitaria": (
        "Ambiente y territorio",
        "es",
        "Cuadernos de Extensión UNLPam",
        ["SIAI", "extensión universitaria", "gestión ambiental"],
    ),
    "Instance retrieval from non-labeled data": (
        "LLM y PLN",
        "en",
        None,
        [
            "clasificación de texto",
            "desbalanceo",
            "correo electrónico",
            "recuperación de instancias",
        ],
    ),
    "Descubrimiento de patrones de comportamiento": (
        "Educación superior",
        "es",
        "WICC",
        ["abandono", "aprendizaje automático", "minería de datos"],
    ),
    "Agrupamiento de Universidades Nacionales": (
        "Educación superior",
        "es",
        "Coloquio de Estadística",
        ["clustering", "estadística", "universidades"],
    ),
    "Herramientas de gestión ambiental sustentable": (
        "Ambiente y territorio",
        "es",
        "Polish-Colombian Symposium",
        ["ordenamiento territorial", "gestión ambiental", "gobiernos locales"],
    ),
    "La automatización de la certificación": (
        "Educación superior",
        "es",
        "RAN",
        ["certificación de títulos", "gestión pública", "acceso a la información"],
    ),
    "Multi-class e-mail classification": (
        "LLM y PLN",
        "en",
        "JCC-BD&ET",
        [
            "clasificación de texto",
            "semi-supervisado",
            "selección de atributos",
            "correo electrónico",
        ],
    ),
    "Clasificación automática de correos electrónicos": (
        "LLM y PLN",
        "es",
        "WICC",
        ["clasificación de texto", "correo electrónico"],
    ),
    "Classic and recent (neural) approaches": (
        "LLM y PLN",
        "en",
        "JCC-BD&ET",
        ["clasificación de texto", "redes neuronales", "español"],
    ),
    "Collaborative, distributed, scalable and low-cost platform": (
        "HPC y cloud",
        "en",
        "Euro-Par",
        ["microservicios", "contenedores", "dispositivos móviles", "cómputo intensivo"],
    ),
    "Plataforma colaborativa, elástica": (
        "HPC y cloud",
        "es",
        "CIbCA",
        ["HPC", "nube", "contenedores", "bajo consumo"],
    ),
    "Collaborative, distributed and scalable platform based on mobile": (
        "HPC y cloud",
        "en",
        "JCC-BD&ET",
        ["microservicios", "contenedores", "móviles", "cómputo intensivo"],
    ),
    "El rendimiento académico de los estudiantes": (
        "Educación superior",
        "es",
        "RETOS XXI",
        ["rendimiento académico", "discapacidad", "inclusión"],
    ),
    "Unconstrained Text Detection in Manga": (
        "Visión por computadora",
        "en",
        "ECCV",
        ["detección de texto", "manga", "segmentación", "dataset"],
    ),
    "Hybrid Elastic ARM": (
        "HPC y cloud",
        "en",
        "JCC-BD&ET",
        ["ARM", "HPC", "nube híbrida", "elasticidad"],
    ),
    "A tool for modeling computational maps": (
        "Visión por computadora",
        "en",
        "NeurIPS",
        ["PyTorch", "corteza visual", "neurociencia computacional", "software libre"],
    ),
    "Bioinspired self organizing neural networks": (
        "Visión por computadora",
        "en",
        "NeurIPS",
        ["redes autoorganizadas", "reconocimiento de expresiones", "bioinspiración"],
    ),
    "Procesamiento distribuido y paralelo de bajo costo": (
        "HPC y cloud",
        "es",
        "CACIC",
        ["procesamiento paralelo", "nube", "móviles", "bajo costo"],
    ),
}

META_PROXIMAS = {
    "Large Language Models actuales": (
        "LLM y PLN",
        "es",
        ["Transformers", "modelos recurrentes", "IA generativa", "arquitecturas de IA"],
    ),
    "Modelos fundacionales geoespaciales": (
        "Ambiente y territorio",
        "es",
        [
            "observación de la Tierra",
            "transferencia de aprendizaje",
            "suelos",
            "Prithvi",
            "TerraMind",
        ],
    ),
}


def _norm(x):
    import unicodedata

    return unicodedata.normalize("NFKD", x).encode("ascii", "ignore").decode().lower()


def buscar_meta(titulo, tabla=META):
    t = _norm(titulo)
    for frag, dato in tabla.items():
        if _norm(frag) in t:
            return dato
    return None


def sede_desde_venue(venue):
    """Fallback cuando META no fija la sede: deducirla del texto del venue."""
    v = _norm(venue)
    for clave, etiqueta in [
        ("cacic", "CACIC"),
        ("wicc", "WICC"),
        ("jcc-bd", "JCC-BD&ET"),
        ("cloud computing, big data", "JCC-BD&ET"),
        ("euro-par", "Euro-Par"),
        ("nips", "NeurIPS"),
        ("eccv", "ECCV"),
        ("ciice", "CIICE"),
        ("nlp school", "NLP School"),
        ("coloquio", "Coloquio de Estadística"),
        ("polish", "Polish-Colombian Symposium"),
        ("eudelar", "EUDELAR"),
        ("iberoamericana", "CIbCA"),
        ("razon critica", "Revista"),
        ("anuario", "Revista"),
        ("cuadernos", "Revista"),
        ("ran", "Revista"),
        ("retos", "Revista"),
    ]:
        if clave in v:
            return etiqueta
    return "Otras"


def autores_lista(autores):
    """'Fernandez, J. M.; Errecalde, M. (eds.)' -> ['Fernandez, J. M.', 'Errecalde, M.']"""
    limpio = autores.replace("(eds.)", "").replace("(ed.)", "")
    # ojo: no recortar el punto final, es parte de la inicial ("Fernandez, J. M.")
    return [a.strip(" ;\n") for a in limpio.split(";") if a.strip(" ;\n")]


def apellido(autor):
    return autor.split(",")[0].strip()
