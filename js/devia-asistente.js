/* Diplomatura en IA Generativa: asistente inmersivo de la portada.
   Vista por defecto: una escena a pantalla completa con un orbe de partículas (el asistente), la constelación de
   las secciones del sitio (sus embeddings proyectados a 3D por PCA) y un fondo de números de embedding reales.
   Al preguntar, el backend (asistente-dev-ia) calcula el embedding de la pregunta, recupera las secciones más
   parecidas y genera la respuesta en streaming; la escena muestra cada etapa y el panel "Ver por dentro" sus datos.
   Arriba a la derecha se pasa al sitio convencional, que sigue en el HTML. Si el backend no responde, la página
   queda como siempre. */
(function () {
    'use strict';
    var API = '/dev-ia/api';
    var CLAVE = 'devia-vista';
    var raiz = document.documentElement;
    var reducir = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var SUGERENCIAS = ['¿Necesito saber programar?', '¿Qué voy a construir?', '¿Cuánto cuesta?',
        '¿Cuándo empieza la próxima cohorte?', '¿Quiénes son los docentes?', '¿Qué título otorga?'];
    var GRUPOS = {
        'dev-ia': ['Portada', '77,226,255'], 'plan-de-estudios': ['Plan de estudios', '138,125,255'],
        'aranceles': ['Aranceles', '255,196,92'], 'requisitos': ['Requisitos', '110,231,160'],
        'destinatarios': ['Destinatarios', '110,231,160'], 'enfoque': ['Enfoque', '255,140,200'],
        'por-que-elegirnos': ['Por qué elegirnos', '255,91,216'], 'inscripcion-dev-ia': ['Inscripción', '120,170,255']
    };

    function leerPref() { try { return localStorage.getItem(CLAVE); } catch (e) { return null; } }
    function guardarPref(v) { try { localStorage.setItem(CLAVE, v); } catch (e) { /* sin almacenamiento */ } }
    function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); }
    var pideSitio = /[?&]vista=sitio/.test(location.search) || location.hash.length > 1 || leerPref() === 'sitio';

    var MAPA = null, porId = {};
    var capa, lienzo, ctx, saludo, mensajes, entrada, texto, enviarBtn, dentro, volver, selector, botonDentro;
    var historia = [], ocupado = false, charlando = false, abierta = false;

    // ---------- Arranque: el asistente solo aparece si el backend responde ----------
    var limite = setTimeout(function () { raiz.classList.remove('da-cargando'); }, 5000);
    fetch(API + '/mapa').then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); }).then(function (m) {
        MAPA = m;
        m.secciones.forEach(function (s) { porId[s.id] = s; });
        construir();
        raiz.classList.add('da-disponible');
        document.addEventListener('click', function (e) {
            var a = e.target.closest('[data-da-abrir]');
            if (!a) return;
            e.preventDefault();
            var menu = document.getElementById('navbarResponsive');
            if (menu && menu.classList.contains('show') && window.bootstrap) window.bootstrap.Collapse.getOrCreateInstance(menu).hide();
            abrir(true);
        });
        if (pideSitio) { volver.classList.add('visible'); } else { abrir(false); }
        clearTimeout(limite);
        raiz.classList.remove('da-cargando');
    }).catch(function () { clearTimeout(limite); raiz.classList.remove('da-cargando'); });

    // ---------- Interfaz ----------
    function construir() {
        capa = document.createElement('div');
        capa.className = 'da';
        capa.hidden = true;
        capa.setAttribute('role', 'region');
        capa.setAttribute('aria-label', 'Asistente de la diplomatura');
        capa.innerHTML =
            '<canvas class="da-lienzo" aria-hidden="true"></canvas>' +
            '<div class="da-barra">' +
            '  <div class="da-marca"><span class="da-logo" aria-hidden="true"><i class="da-logo-anillo"></i><i class="da-logo-centro"></i></span><span class="da-marca-txt">' +
            '    <strong>Diplomatura en IA Generativa en la Nube</strong><span>Asistente · LICDIA · UNLu</span></span></div>' +
            '  <div class="da-acciones">' +
            '    <button type="button" class="da-boton-dentro" aria-pressed="false"><span class="da-ojo"></span><span class="da-dentro-txt">Ver por dentro</span></button>' +
            '    <div class="da-selector" role="group" aria-label="Vista de la página">' +
            '      <button type="button" data-v="asistente" aria-pressed="true">Asistente</button>' +
            '      <button type="button" data-v="sitio" aria-pressed="false">Sitio convencional</button></div>' +
            '  </div>' +
            '</div>' +
            '<div class="da-saludo"><h1></h1><p></p></div>' +
            '<aside class="da-dentro" aria-label="Cómo responde el asistente">' +
            '  <h2>Cómo responde</h2>' +
            '  <p>Es un RAG (generación aumentada por recuperación), el tipo de sistema que se construye en la diplomatura. ' +
            '     Cada paso se actualiza con tu pregunta.</p>' +
            '  <div class="da-paso" data-n="1" data-paso="emb"><h3>Embedding de la pregunta</h3>' +
            '    <div><span class="da-dato" data-c="emb-modelo"></span> · <span class="da-dato" data-c="dims"></span> dimensiones · <span class="da-dato" data-c="emb-ms">–</span> ms</div>' +
            '    <div class="da-vector"></div><div class="da-vector-num">Hacé una pregunta para ver su vector.</div></div>' +
            '  <div class="da-paso" data-n="2" data-paso="rec"><h3>Recuperación</h3>' +
            '    <div>Similitud coseno contra las <span class="da-dato" data-c="n-sec"></span> secciones del sitio; pasan las <span class="da-dato" data-c="k"></span> más cercanas.</div>' +
            '    <table class="da-tabla"></table><div class="da-leyenda"></div></div>' +
            '  <div class="da-paso" data-n="3" data-paso="gen"><h3>Generación</h3>' +
            '    <div>Modelo <span class="da-dato" data-c="llm"></span></div>' +
            '    <div>Prompt: reglas + secciones + conversación · <span class="da-dato" data-c="tok-in">–</span> tokens</div>' +
            '    <div>Primer token <span class="da-dato" data-c="ttft">–</span> ms · respuesta <span class="da-dato" data-c="tok-out">–</span> tokens · <span class="da-dato" data-c="tps">–</span> tokens/s</div></div>' +
            '  <div class="da-paso" data-n="4" data-paso="cit"><h3>Citas</h3>' +
            '    <div>Cada afirmación lleva el número de la sección de la que sale. Al tocarlo vas a esa parte del sitio.</div></div>' +
            '</aside>' +
            '<div class="da-charla">' +
            '  <div class="da-mensajes" aria-live="polite"></div>' +
            '  <form class="da-entrada"><textarea rows="1" aria-label="Escribí tu pregunta" maxlength="600"></textarea>' +
            '    <button class="da-enviar" type="submit" aria-label="Enviar">&#8594;</button></form>' +
            '  <div class="da-sugerencias"></div>' +
            '  <p class="da-aviso">Respuestas generadas con IA a partir del contenido de este sitio. Pueden tener errores: verificá en la sección citada. Las preguntas no se guardan.</p>' +
            '</div>';
        document.body.appendChild(capa);

        lienzo = capa.querySelector('.da-lienzo');
        ctx = lienzo.getContext('2d');
        saludo = capa.querySelector('.da-saludo');
        mensajes = capa.querySelector('.da-mensajes');
        entrada = capa.querySelector('.da-entrada');
        texto = entrada.querySelector('textarea');
        enviarBtn = entrada.querySelector('.da-enviar');
        dentro = capa.querySelector('.da-dentro');
        selector = capa.querySelector('.da-selector');
        botonDentro = capa.querySelector('.da-boton-dentro');

        dato('emb-modelo', MAPA.modelo_embeddings.split('/').pop());
        dato('dims', MAPA.dimensiones);
        dato('n-sec', MAPA.secciones.length);
        dato('k', MAPA.k);
        dato('llm', MAPA.modelo || '—');
        var vec = capa.querySelector('.da-vector');
        for (var i = 0; i < 128; i++) vec.appendChild(document.createElement('span'));
        var usados = {};
        MAPA.secciones.forEach(function (s) { usados[s.pagina] = 1; });
        capa.querySelector('.da-leyenda').innerHTML = Object.keys(GRUPOS).filter(function (g) { return usados[g]; }).map(function (g) {
            return '<span><i style="background:rgb(' + GRUPOS[g][1] + ')"></i>' + GRUPOS[g][0] + '</span>';
        }).join('');

        var sug = capa.querySelector('.da-sugerencias');
        SUGERENCIAS.forEach(function (q) {
            var b = document.createElement('button');
            b.type = 'button';
            b.textContent = q;
            b.addEventListener('click', function () { enviar(q); });
            sug.appendChild(b);
        });

        entrada.addEventListener('submit', function (e) { e.preventDefault(); enviar(texto.value); });
        texto.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) { e.preventDefault(); enviar(texto.value); }
        });
        texto.addEventListener('input', ajustarAlto);
        selector.addEventListener('click', function (e) {
            var b = e.target.closest('button');
            if (!b) return;
            if (b.getAttribute('data-v') === 'sitio') cerrar(true); else abrir(true);
        });
        botonDentro.addEventListener('click', function () {
            var ab = !dentro.classList.contains('abierto');
            dentro.classList.toggle('abierto', ab);
            botonDentro.setAttribute('aria-pressed', ab ? 'true' : 'false');
            ubicarEscena();
        });
        mensajes.addEventListener('click', function (e) {
            var a = e.target.closest('[data-id]');
            if (!a) return;
            e.preventDefault();
            ir(a.getAttribute('data-id'));
        });
        mensajes.addEventListener('mouseover', function (e) {
            var a = e.target.closest('[data-id]');
            resaltado = a ? a.getAttribute('data-id') : null;
        });

        volver = document.createElement('button');
        volver.type = 'button';
        volver.className = 'da-volver';
        volver.innerHTML = '<span class="da-logo" aria-hidden="true"><i class="da-logo-anillo"></i><i class="da-logo-centro"></i></span>Volver al asistente';
        volver.addEventListener('click', function () { abrir(true); });
        document.body.appendChild(volver);

        prepararEscena();
        window.addEventListener('resize', function () { medir(); ubicarEscena(); });
        document.addEventListener('visibilitychange', function () { if (!document.hidden) arrancar(); });
        capa.addEventListener('pointermove', function (e) {
            raton.x = (e.clientX / W) * 2 - 1;
            raton.y = (e.clientY / H) * 2 - 1;
        });
    }

    function dato(c, v) { var el = capa.querySelector('[data-c="' + c + '"]'); if (el) el.textContent = v; }
    function ajustarAlto() {
        texto.style.height = 'auto';
        texto.style.height = Math.min(texto.scrollHeight, 140) + 'px';
        texto.style.overflowY = texto.scrollHeight > 140 ? 'auto' : 'hidden';
    }

    function abrir(porUsuario) {
        capa.hidden = false;
        raiz.classList.add('da-on');
        volver.classList.remove('visible');
        selector.querySelectorAll('button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-v') === 'asistente' ? 'true' : 'false'); });
        if (porUsuario) guardarPref('asistente');
        abierta = true;
        medir();
        ubicarEscena(true);
        requestAnimationFrame(function () { capa.classList.add('visible'); });
        arrancar();
        if (!saludo.dataset.listo) { saludo.dataset.listo = '1'; saludar(); }
        setTimeout(function () { if (window.matchMedia('(pointer: fine)').matches) texto.focus({ preventScroll: true }); }, 400);
    }
    function cerrar(porUsuario) {
        capa.classList.remove('visible');
        abierta = false;
        if (porUsuario) guardarPref('sitio');
        setTimeout(function () { if (!abierta) { capa.hidden = true; raiz.classList.remove('da-on'); } }, reducir ? 0 : 450);
        volver.classList.add('visible');
    }

    // Saludo escrito token a token (trozos de 2 a 5 letras, como los de un tokenizador)
    function tokens(s) {
        var out = [], r = 7;
        s.split(/(\s+)/).forEach(function (w) {
            if (/^\s+$/.test(w) || w.length <= 4) { out.push(w); return; }
            for (var i = 0; i < w.length;) { r = (r * 16807) % 2147483647; var n = 2 + (r % 4); out.push(w.slice(i, i + n)); i += n; }
        });
        return out;
    }
    function escribir(el, s, ms, listo) {
        if (reducir) { el.textContent = s; if (listo) listo(); return; }
        var t = tokens(s), i = 0, cur = document.createElement('span');
        cur.className = 'da-cursor';
        el.textContent = '';
        var txt = document.createTextNode('');
        el.appendChild(txt);
        el.appendChild(cur);
        (function paso() {
            if (i >= t.length) { cur.remove(); if (listo) listo(); return; }
            txt.data += t[i++];
            pulso = Math.min(1, pulso + 0.12);
            setTimeout(paso, ms * (0.6 + Math.random() * 0.8));
        })();
    }
    function saludar() {
        var h = saludo.querySelector('h1'), p = saludo.querySelector('p');
        setTimeout(function () {
            escribir(h, 'Hola. Soy el asistente de la diplomatura.', 45, function () {
                escribir(p, 'Preguntame lo que quieras sobre la cursada, los contenidos o la inscripción. Respondo con la información de este sitio y te muestro cómo lo hago.', 22);
            });
        }, reducir ? 0 : 700);
        var k = 0;
        texto.placeholder = 'Escribí tu pregunta…';
        setInterval(function () {
            if (texto.value || charlando) return;
            var q = SUGERENCIAS[k++ % SUGERENCIAS.length];
            texto.placeholder = W < 560 ? q : 'Por ejemplo: ' + q;
        }, 3500);
    }

    // ---------- Conversación ----------
    function enviar(q) {
        q = (q || '').trim();
        if (!q || ocupado) return;
        if (!charlando) { charlando = true; capa.classList.add('charlando'); ubicarEscena(); }
        ocupado = true;
        enviarBtn.disabled = true;
        var u = document.createElement('div');
        u.className = 'da-msj da-msj-usuario';
        u.textContent = q;
        mensajes.appendChild(u);
        historia.push({ rol: 'usuario', texto: q });
        var m = document.createElement('div');
        m.className = 'da-msj da-msj-asistente';
        m.innerHTML = '<div class="da-estado"><i></i><span>Calculando el embedding de tu pregunta…</span></div>';
        mensajes.appendChild(m);
        mensajes.scrollTop = mensajes.scrollHeight;
        var r = texto.getBoundingClientRect();
        origen = { x: r.left + 40, y: r.top + r.height / 2, w: Math.max(80, r.width - 80) };
        texto.value = '';
        ajustarAlto();
        estado = 'pensando';
        pregunta = null; sims = null; top = []; vuelos = []; t_sec = 0;
        marcarPaso('emb');

        var acumulado = '', citas = { orden: [], num: {} }, fin = null, t_inicio = performance.now();
        fetch(API + '/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ mensajes: historia.slice(-9) })
        }).then(function (res) {
            if (!res.ok || !res.body) throw new Error(res.status);
            return leerSSE(res.body, function (ev, d) {
                if (ev === 'embedding') {
                    lanzarNumeros(d.valores);
                    pregunta = { xyz: d.xyz, t: performance.now() };
                    dato('emb-ms', d.ms);
                    pintarVector(d.valores);
                    estadoMsj(m, 'Buscando las secciones más parecidas…');
                    marcarPaso('rec');
                } else if (ev === 'secciones') {
                    sims = d.todas;
                    top = d.top.map(function (x) { return x.id; });
                    t_sec = performance.now();
                    pintarTabla(d.top, d.todas);
                    estadoMsj(m, 'Generando la respuesta con ' + d.top.length + ' secciones del sitio…');
                    marcarPaso('gen');
                } else if (ev === 'texto') {
                    if (!acumulado) { estado = 'hablando'; m.innerHTML = '<div class="da-cuerpo"></div>'; }
                    acumulado += d.t;
                    pulso = Math.min(1, pulso + 0.3);
                    m.firstChild.innerHTML = formatear(acumulado, citas, true);
                    seguir();
                } else if (ev === 'fin') {
                    fin = d;
                } else if (ev === 'error') {
                    throw new Error('modelo');
                }
            });
        }).then(function () {
            if (!acumulado) throw new Error('vacío');
            m.firstChild.innerHTML = formatear(acumulado, citas, false);
            m.appendChild(fuentes(citas));
            historia.push({ rol: 'asistente', texto: acumulado });
            if (fin) {
                dato('tok-in', fin.tokens_entrada != null ? fin.tokens_entrada.toLocaleString('es-AR') : '—');
                dato('tok-out', fin.tokens_salida != null ? fin.tokens_salida : '—');
                dato('ttft', fin.ms_primer_token != null ? fin.ms_primer_token : '—');
                var seg = (fin.ms_generacion - (fin.ms_primer_token || 0)) / 1000;
                dato('tps', fin.tokens_salida && seg > 0 ? Math.round(fin.tokens_salida / seg) : '—');
            }
            marcarPaso('cit');
            seguir();
        }).catch(function () {
            historia.pop();
            m.innerHTML = '<div class="da-error">No pude responder en este momento.<br><button type="button">Ver el sitio convencional</button></div>';
            m.querySelector('button').addEventListener('click', function () { cerrar(false); });
        }).then(function () {
            ocupado = false;
            enviarBtn.disabled = false;
            estado = 'reposo';
            void t_inicio;
        });
    }

    function seguir() {
        if (mensajes.scrollHeight - mensajes.scrollTop - mensajes.clientHeight < 160) mensajes.scrollTop = mensajes.scrollHeight;
    }
    function estadoMsj(m, s) { var e = m.querySelector('.da-estado span'); if (e) e.textContent = s; }
    function marcarPaso(p) {
        capa.querySelectorAll('.da-paso').forEach(function (x) { x.classList.toggle('activo', x.getAttribute('data-paso') === p); });
    }

    function leerSSE(cuerpo, cb) {
        var lector = cuerpo.getReader(), dec = new TextDecoder(), buf = '';
        function paso() {
            return lector.read().then(function (r) {
                if (r.done) return;
                buf += dec.decode(r.value, { stream: true });
                var i;
                while ((i = buf.indexOf('\n\n')) >= 0) {
                    var bloque = buf.slice(0, i), ev = 'message', data = '';
                    buf = buf.slice(i + 2);
                    bloque.split('\n').forEach(function (l) {
                        if (l.indexOf('event:') === 0) ev = l.slice(6).trim();
                        else if (l.indexOf('data:') === 0) data += l.slice(5).trim();
                    });
                    if (data) cb(ev, JSON.parse(data));
                }
                return paso();
            });
        }
        return paso();
    }

    function numero(citas, id) {
        if (!porId[id]) return 0;
        if (!citas.num[id]) { citas.orden.push(id); citas.num[id] = citas.orden.length; }
        return citas.num[id];
    }
    function formatear(txt, citas, enCurso) {
        if (enCurso) txt = txt.replace(/\[[^\]]{0,12}$/, '');   // una cita que todavía no terminó de llegar
        var h = esc(txt).replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        h = h.replace(/\[((?:S\d+[\s,;]*)+)\]/g, function (_, g) {
            return g.split(/[\s,;]+/).filter(Boolean).map(function (id) {
                var n = numero(citas, id);
                return n ? '<a class="da-cita" href="#" data-id="' + id + '" title="' + esc(porId[id].titulo) + '">' + n + '</a>' : '';
            }).join('');
        });
        var out = [], lista = null;
        h.split('\n').forEach(function (l) {
            var li = l.match(/^\s*(?:[-*•]|\d+[.)])\s+(.*)$/);
            if (li) { (lista = lista || []).push('<li>' + li[1] + '</li>'); return; }
            if (lista) { out.push('<ul>' + lista.join('') + '</ul>'); lista = null; }
            if (l.trim()) out.push('<p>' + l + '</p>');
        });
        if (lista) out.push('<ul>' + lista.join('') + '</ul>');
        var html = out.join('');
        if (enCurso) html = html.replace(/(<\/(?:p|li)>(?:<\/ul>)?)$/, '<span class="da-cursor"></span>$1');
        return html;
    }
    function fuentes(citas) {
        var ids = citas.orden.length ? citas.orden : top.slice(0, 3);
        var d = document.createElement('div');
        d.className = 'da-fuentes';
        d.innerHTML = ids.map(function (id, i) {
            var s = porId[id];
            return '<a class="da-fuente" href="' + esc(destino(s)) + '" data-id="' + id + '"><b>' + (citas.orden.length ? i + 1 : id) + '</b>' + esc(corto(s.titulo, 48)) + '</a>';
        }).join('');
        return d;
    }
    function corto(s, n) { s = s.replace(/^Preguntas Frecuentes: /, ''); return s.length > n ? s.slice(0, n - 1) + '…' : s; }
    function destino(s) { return s.url + (s.ancla ? '#' + s.ancla : ''); }
    function estaEnPortada(s) { return s.url === '/dev-ia/' && /\/dev-ia\/(index\.html)?$/.test(location.pathname); }

    // Ir a la sección citada: en la portada se pasa al sitio convencional y se resalta; si no, se navega
    function ir(id) {
        var s = porId[id];
        if (!s) return;
        if (!estaEnPortada(s)) { location.href = destino(s); return; }
        cerrar(false);
        var el = s.ancla && document.getElementById(s.ancla);
        if (!el) return;
        if (el.classList.contains('collapse') && window.bootstrap) window.bootstrap.Collapse.getOrCreateInstance(el, { toggle: false }).show();
        var blanco = el.closest('.accordion-item') || el;
        setTimeout(function () {
            blanco.scrollIntoView({ behavior: reducir ? 'auto' : 'smooth', block: 'center' });
            blanco.classList.remove('da-resaltada');
            void blanco.offsetWidth;
            blanco.classList.add('da-resaltada');
        }, reducir ? 0 : 480);
    }

    function pintarVector(v) {
        var celdas = capa.querySelectorAll('.da-vector span');
        v.slice(0, 128).forEach(function (x, i) {
            var a = Math.min(1, Math.abs(x) / 0.08);
            celdas[i].style.background = x >= 0 ? 'rgba(77,226,255,' + a.toFixed(2) + ')' : 'rgba(138,125,255,' + a.toFixed(2) + ')';
        });
        capa.querySelector('.da-vector-num').textContent = '[' + v.slice(0, 24).map(function (x) { return x.toFixed(3); }).join(', ') + ', … ]';
    }
    // Las barras van del mínimo al máximo de la similitud contra todas las secciones (cada modelo tiene su escala)
    function pintarTabla(lista, todas) {
        var lo = Math.min.apply(null, todas), hi = Math.max.apply(null, todas);
        capa.querySelector('.da-tabla').innerHTML = lista.map(function (x) {
            var s = porId[x.id], g = GRUPOS[s.pagina] || GRUPOS['dev-ia'];
            return '<tr><td>' + x.id + '</td><td><span style="color:rgb(' + g[1] + ')">●</span> ' + esc(corto(s.titulo, 34)) +
                '</td><td>' + x.sim.toFixed(3) + '</td><td><div class="da-barra-sim"><i style="width:' + Math.max(4, Math.round((x.sim - lo) / Math.max(1e-6, hi - lo) * 100)) + '%"></i></div></td></tr>';
        }).join('');
    }

    // ---------- Escena ----------
    var W = 0, H = 0, dpr = 1, U = 1;
    var esc3 = { cx: 0, cy: 0, k: 1, cxO: 0, cyO: 0, kO: 1 };
    var raton = { x: 0, y: 0, sx: 0, sy: 0 };
    var estado = 'reposo', pulso = 0, corriendo = false, t_prev = 0, giro = 0;
    var ORBE = [], NODOS = [], ARISTAS = [], NUMS = [], vuelos = [], chispas = [];
    var pregunta = null, sims = null, top = [], t_sec = 0, origen = null, resaltado = null;

    function prepararEscena() {
        var N = 520, oro = Math.PI * (3 - Math.sqrt(5));
        for (var i = 0; i < N; i++) {
            var y = 1 - (i / (N - 1)) * 2, r = Math.sqrt(1 - y * y), th = i * oro;
            ORBE.push({ x: Math.cos(th) * r, y: y, z: Math.sin(th) * r, f: Math.random() * 6.283 });
        }
        NODOS = MAPA.secciones.map(function (s) {
            var e = empujar(s.xyz);
            return { id: s.id, x: e.x, y: e.y, z: e.z, col: (GRUPOS[s.pagina] || GRUPOS['dev-ia'])[1], titulo: s.titulo };
        });
        var vistos = {};
        NODOS.forEach(function (a, i) {
            var d = NODOS.map(function (b, j) { return [j, (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y) + (a.z - b.z) * (a.z - b.z)]; })
                .sort(function (p, q) { return p[1] - q[1]; });
            for (var k = 1; k <= 2; k++) {
                var j = d[k][0], clave = Math.min(i, j) + '-' + Math.max(i, j);
                if (!vistos[clave]) { vistos[clave] = 1; ARISTAS.push([i, j]); }
            }
        });
        var muestra = MAPA.muestra || [];
        for (var n = 0; n < 64; n++) {
            var v = muestra[n % Math.max(1, muestra.length)] || 0;
            NUMS.push({ txt: (v >= 0 ? '+' : '') + v.toFixed(4), x: Math.random() * 2 - 1, y: Math.random() * 2 - 1, z: Math.random(),
                vx: (Math.random() - 0.5) * 0.0004, vy: -0.0002 - Math.random() * 0.0004 });
        }
        medir();
    }

    // Corre cada punto hacia afuera (misma dirección, radio 0,42 + 0,58·r) para que no quede tapado por el orbe
    function empujar(v) {
        var r = Math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2]) || 1e-6, f = (0.42 + 0.58 * Math.min(r, 1.2)) / r;
        return { x: v[0] * f, y: v[1] * f, z: v[2] * f };
    }

    function medir() {
        if (!lienzo) return;
        dpr = Math.min(window.devicePixelRatio || 1, 2);
        W = capa.clientWidth || window.innerWidth;
        H = capa.clientHeight || window.innerHeight;
        U = Math.min(W * 1.1, H);
        lienzo.width = Math.round(W * dpr);
        lienzo.height = Math.round(H * dpr);
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }

    // Dónde va la escena según el momento: centrada al inicio; a la izquierda de la charla en escritorio
    function ubicarEscena(inmediato) {
        var ancho = W >= 992, panel = dentro && dentro.classList.contains('abierto') ? Math.min(380, W - 24) + 30 : 0;
        if (!charlando) {
            esc3.cxO = ancho ? (panel + W) / 2 : W / 2; esc3.cyO = H * (ancho ? 0.31 : 0.23); esc3.kO = ancho ? 1 : 0.85;
            if (!ancho && H < 520) { esc3.cyO = H * 0.17; esc3.kO = 0.42; }
        } else if (ancho) {
            var izqCharla = W - Math.min(600, W * 0.44) - Math.max(16, Math.min(56, W * 0.04));
            esc3.cxO = (panel + izqCharla) / 2; esc3.cyO = H * 0.53; esc3.kO = panel ? 0.85 : 1.08;
        } else {
            esc3.cxO = W / 2; esc3.cyO = H * 0.2; esc3.kO = H < 520 ? 0.4 : 0.55;
        }
        if (inmediato) { esc3.cx = esc3.cxO; esc3.cy = esc3.cyO; esc3.k = esc3.kO; }
    }

    function arrancar() {
        if (corriendo || !abierta) return;
        corriendo = true;
        t_prev = performance.now();
        requestAnimationFrame(cuadro);
    }

    function rot(p, a, b) {
        var ca = Math.cos(a), sa = Math.sin(a), cb = Math.cos(b), sb = Math.sin(b);
        var x = p.x * ca - p.z * sa, z = p.x * sa + p.z * ca;
        return { x: x, y: p.y * cb - z * sb, z: p.y * sb + z * cb };
    }
    function proy(p, R) {
        var s = 3 / (3 + p.z);
        return { x: esc3.cx + p.x * R * s, y: esc3.cy + p.y * R * s, s: s, z: p.z };
    }

    function lanzarNumeros(valores) {
        if (!origen || reducir) return;
        var cr = capa.getBoundingClientRect(), ahora = performance.now();
        valores.slice(0, 96).forEach(function (v, i) {
            vuelos.push({ txt: (v >= 0 ? '+' : '') + v.toFixed(3), x0: origen.x - cr.left - origen.w / 2 + Math.random() * origen.w,
                y0: origen.y - cr.top + (Math.random() - 0.5) * 20, t0: ahora + i * 14, dur: 1100 + Math.random() * 700,
                cx: (Math.random() - 0.5) * 260, cy: -120 - Math.random() * 160 });
        });
    }

    function cuadro(ahora) {
        if (!abierta || document.hidden) { corriendo = false; return; }
        var dt = Math.min(50, ahora - t_prev);
        t_prev = ahora;
        var t = ahora / 1000;
        esc3.cx += (esc3.cxO - esc3.cx) * 0.06;
        esc3.cy += (esc3.cyO - esc3.cy) * 0.06;
        esc3.k += (esc3.kO - esc3.k) * 0.06;
        raton.sx += (raton.x - raton.sx) * 0.04;
        raton.sy += (raton.y - raton.sy) * 0.04;
        var vel = estado === 'pensando' ? 3.2 : estado === 'hablando' ? 1.8 : 1;
        giro += dt * 0.00012 * vel;
        pulso *= 0.94;
        var A = giro + raton.sx * 0.35, B = 0.32 + raton.sy * 0.18;
        var Rorbe = U * 0.075 * esc3.k, Rmapa = U * 0.34 * esc3.k;

        ctx.clearRect(0, 0, W, H);

        // 1. Fondo de números (valores reales de los embeddings de las secciones)
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        NUMS.forEach(function (n) {
            n.x += n.vx * dt * (estado === 'pensando' ? 2.5 : 1);
            n.y += n.vy * dt * (estado === 'pensando' ? 2.5 : 1);
            if (n.y < -1.15) { n.y = 1.15; n.x = Math.random() * 2 - 1; }
            if (n.x < -1.15) n.x = 1.15; else if (n.x > 1.15) n.x = -1.15;
            var px = W / 2 + n.x * W * 0.55 - raton.sx * 30 * n.z, py = H / 2 + n.y * H * 0.55 - raton.sy * 20 * n.z;
            ctx.font = '400 ' + (9 + n.z * 6).toFixed(1) + 'px "DM Mono", ui-monospace, monospace';
            ctx.fillStyle = 'rgba(150,200,255,' + (0.04 + n.z * 0.16).toFixed(3) + ')';
            ctx.fillText(n.txt, px, py);
        });

        // 2. Constelación de secciones
        var P = NODOS.map(function (n) { return proy(rot(n, A * 0.6, B), Rmapa); });
        var smin = 1, smax = 0;
        if (sims) sims.forEach(function (s) { if (s < smin) smin = s; if (s > smax) smax = s; });
        function luz(i) { if (!sims) return 0.35; var u = (sims[i] - smin) / Math.max(1e-6, smax - smin); return 0.08 + 0.92 * u * u * u; }
        ctx.lineWidth = 1;
        ARISTAS.forEach(function (e) {
            var a = P[e[0]], b = P[e[1]], al = 0.05 + 0.12 * Math.min(luz(e[0]), luz(e[1]));
            ctx.strokeStyle = 'rgba(140,180,255,' + al.toFixed(3) + ')';
            ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke();
        });
        NODOS.forEach(function (n, i) {
            var p = P[i], l = luz(i), r = (1.4 + 2.2 * p.s * (0.6 + l)) * (esc3.k > 0.7 ? 1 : 0.8);
            var esTop = top.indexOf(n.id) >= 0;
            if (esTop || n.id === resaltado) {
                var g = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 7);
                g.addColorStop(0, 'rgba(' + n.col + ',.55)'); g.addColorStop(1, 'rgba(' + n.col + ',0)');
                ctx.fillStyle = g; ctx.beginPath(); ctx.arc(p.x, p.y, r * 7, 0, 6.283); ctx.fill();
            }
            ctx.fillStyle = 'rgba(' + n.col + ',' + Math.min(1, 0.25 + l).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(p.x, p.y, esTop ? r * 1.5 : r, 0, 6.283); ctx.fill();
            if (n.id === resaltado) {
                ctx.strokeStyle = 'rgba(255,255,255,.9)'; ctx.lineWidth = 1.5;
                ctx.beginPath(); ctx.arc(p.x, p.y, r * 3.2 + Math.sin(t * 6) * 1.5, 0, 6.283); ctx.stroke(); ctx.lineWidth = 1;
            }
        });

        // 3. La pregunta en el mismo espacio, los haces hacia las secciones recuperadas y el flujo hacia el orbe
        var Q = null;
        if (pregunta) {
            Q = proy(rot(empujar(pregunta.xyz), A * 0.6, B), Rmapa);
            var edad = (ahora - pregunta.t) / 1000, rq = 4 + Math.sin(t * 5) * 1.2;
            var gq = ctx.createRadialGradient(Q.x, Q.y, 0, Q.x, Q.y, 34);
            gq.addColorStop(0, 'rgba(255,255,255,.95)'); gq.addColorStop(0.25, 'rgba(255,91,216,.5)'); gq.addColorStop(1, 'rgba(255,91,216,0)');
            ctx.fillStyle = gq; ctx.beginPath(); ctx.arc(Q.x, Q.y, 34, 0, 6.283); ctx.fill();
            ctx.fillStyle = '#fff'; ctx.beginPath(); ctx.arc(Q.x, Q.y, rq, 0, 6.283); ctx.fill();
            if (edad < 1.2) {
                ctx.strokeStyle = 'rgba(255,91,216,' + (1 - edad / 1.2).toFixed(3) + ')';
                ctx.beginPath(); ctx.arc(Q.x, Q.y, 8 + edad * 90, 0, 6.283); ctx.stroke();
            }
            etiqueta('tu pregunta', Q.x, Q.y - 22, 'rgba(255,190,240,.95)', 'center');
            if (t_sec) {
                var avance = Math.min(1, (ahora - t_sec) / 900);
                top.forEach(function (id, k) {
                    var i = NODOS.findIndex(function (n) { return n.id === id; }), p = P[i];
                    var f = Math.max(0, Math.min(1, avance * 1.6 - k * 0.12));
                    if (f <= 0) return;
                    var x = Q.x + (p.x - Q.x) * f, y = Q.y + (p.y - Q.y) * f;
                    var gl = ctx.createLinearGradient(Q.x, Q.y, x, y);
                    gl.addColorStop(0, 'rgba(255,91,216,.85)'); gl.addColorStop(1, 'rgba(' + NODOS[i].col + ',.9)');
                    ctx.strokeStyle = gl; ctx.lineWidth = 1.6;
                    ctx.beginPath(); ctx.moveTo(Q.x, Q.y); ctx.lineTo(x, y); ctx.stroke(); ctx.lineWidth = 1;
                    if (f >= 1 && esc3.k > 0.7) {
                        var lado = p.x >= esc3.cx ? 1 : -1;
                        etiqueta(id + ' · ' + corto(NODOS[i].titulo, 30) + ' · ' + sims[i].toFixed(2), p.x + lado * 10, p.y - 10 + (k % 2 ? 12 : 0),
                            'rgba(' + NODOS[i].col + ',.95)', lado > 0 ? 'left' : 'right');
                    }
                    // contexto que fluye de la sección al orbe
                    if (f >= 1 && estado !== 'reposo' && Math.random() < 0.35) chispas.push({ x: p.x, y: p.y, col: NODOS[i].col, v: 0 });
                });
            }
        }
        chispas = chispas.filter(function (c) {
            c.v = Math.min(1, c.v + dt * 0.0011);
            var e = c.v * c.v, x = c.x + (esc3.cx - c.x) * e, y = c.y + (esc3.cy - c.y) * e;
            ctx.fillStyle = 'rgba(' + c.col + ',' + (0.9 * (1 - c.v)).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(x, y, 1.6, 0, 6.283); ctx.fill();
            if (c.v >= 1) pulso = Math.min(1, pulso + 0.02);
            return c.v < 1;
        });

        // 4. El orbe (el asistente)
        var halo = ctx.createRadialGradient(esc3.cx, esc3.cy, 0, esc3.cx, esc3.cy, Rorbe * 3.2);
        halo.addColorStop(0, 'rgba(77,226,255,' + (0.22 + 0.35 * pulso).toFixed(3) + ')');
        halo.addColorStop(0.45, 'rgba(138,125,255,' + (0.1 + 0.15 * pulso).toFixed(3) + ')');
        halo.addColorStop(1, 'rgba(138,125,255,0)');
        ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(esc3.cx, esc3.cy, Rorbe * 3.2, 0, 6.283); ctx.fill();
        var aO = giro * 2.4 + raton.sx * 0.5, bO = 0.4 + raton.sy * 0.25;
        ORBE.forEach(function (o) {
            var amp = 1 + 0.035 * Math.sin(t * 1.4) + (estado === 'pensando' ? 0.06 * Math.sin(t * 7 + o.f * 3) : 0) + 0.22 * pulso * Math.sin(o.f * 5 + t * 9);
            var q = rot({ x: o.x * amp, y: o.y * amp, z: o.z * amp }, aO, bO), p = proy(q, Rorbe);
            var prof = (1 - q.z) / 2, mezcla = (o.y + 1) / 2;
            var r = Math.round(77 + (138 - 77) * mezcla), g = Math.round(226 + (125 - 226) * mezcla);
            ctx.fillStyle = 'rgba(' + r + ',' + g + ',255,' + (0.18 + 0.8 * prof).toFixed(3) + ')';
            ctx.beginPath(); ctx.arc(p.x, p.y, 0.6 + 1.5 * prof * esc3.k, 0, 6.283); ctx.fill();
        });
        var nucleo = ctx.createRadialGradient(esc3.cx, esc3.cy, 0, esc3.cx, esc3.cy, Rorbe * 0.6);
        nucleo.addColorStop(0, 'rgba(255,255,255,' + (0.35 + 0.5 * pulso).toFixed(3) + ')');
        nucleo.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = nucleo; ctx.beginPath(); ctx.arc(esc3.cx, esc3.cy, Rorbe * 0.6, 0, 6.283); ctx.fill();
        var rotulo = estado === 'pensando' ? (t_sec ? 'recuperando contexto' : pregunta ? 'embedding listo' : 'calculando embedding')
            : estado === 'hablando' ? 'generando · ' + (MAPA.modelo || 'LLM') : MAPA.modelo_embeddings.split('/').pop() + ' · ' + MAPA.dimensiones + ' d';
        etiqueta(rotulo, esc3.cx, esc3.cy + Rorbe * 1.9, 'rgba(160,220,255,.75)', 'center');

        // 5. Los números del embedding de la pregunta vuelan hacia su lugar en el mapa
        if (vuelos.length) {
            var destinoQ = Q || { x: esc3.cx, y: esc3.cy };
            ctx.font = '500 11px "DM Mono", ui-monospace, monospace';
            ctx.textAlign = 'center';
            vuelos = vuelos.filter(function (v) {
                var u = (ahora - v.t0) / v.dur;
                if (u < 0) return true;
                if (u >= 1) { pulso = Math.min(1, pulso + 0.01); return false; }
                var e = u < 0.5 ? 2 * u * u : 1 - Math.pow(-2 * u + 2, 2) / 2;
                var mx = (v.x0 + destinoQ.x) / 2 + v.cx, my = (v.y0 + destinoQ.y) / 2 + v.cy;
                var x = (1 - e) * (1 - e) * v.x0 + 2 * (1 - e) * e * mx + e * e * destinoQ.x;
                var y = (1 - e) * (1 - e) * v.y0 + 2 * (1 - e) * e * my + e * e * destinoQ.y;
                ctx.fillStyle = 'rgba(' + (u < 0.5 ? '200,235,255' : '255,180,240') + ',' + (Math.min(1, u * 6) * (1 - u * u)).toFixed(3) + ')';
                ctx.fillText(v.txt, x, y);
                return true;
            });
        }

        if (reducir && !vuelos.length && !chispas.length) { corriendo = false; return; }
        requestAnimationFrame(cuadro);
    }

    function zonaLibre() {
        var izq = 8, der = W - 8;
        if (dentro.classList.contains('abierto')) izq = Math.min(380, W - 24) + 40;
        if (charlando && W >= 992) der = W - Math.min(600, W * 0.44) - Math.max(16, Math.min(56, W * 0.04)) - 12;
        return [izq, der];
    }
    function etiqueta(s, x, y, color, alin) {
        ctx.font = '500 11px "DM Mono", ui-monospace, monospace';
        ctx.textAlign = 'left';
        ctx.textBaseline = 'middle';
        var w = ctx.measureText(s).width, z = zonaLibre();
        var x0 = alin === 'center' ? x - w / 2 : alin === 'right' ? x - w : x;
        x0 = Math.max(z[0], Math.min(x0, z[1] - w));
        ctx.fillStyle = 'rgba(3,7,18,.6)';
        ctx.fillRect(x0 - 4, y - 8, w + 8, 16);
        ctx.fillStyle = color;
        ctx.fillText(s, x0, y);
    }
})();
