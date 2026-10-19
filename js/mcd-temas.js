/* Maestría en Ciencia de Datos: mapa "Temas de la maestría".
   Lee la lista que genera tools/maestria/temas.py (data-x, data-y en [0, 1] según t-SNE; data-c = curso;
   data-t = tema; data-ctx = encabezado del que forma parte) y dibuja un diagrama de dispersión en SVG.
   Las etiquetas se ubican sin superponerse; las que no entran se ven al pasar el puntero o al filtrar por curso.
   La lista queda en el HTML para lectores de pantalla y buscadores; el gráfico es solo visual. */
(function () {
    var caja = document.querySelector('.mcd-temas');
    if (!caja) return;
    var grafico = caja.querySelector('.mcd-temas-grafico');
    var filtro = caja.querySelector('.mcd-temas-filtro');
    var SVG = 'http://www.w3.org/2000/svg';
    var nombres = {};
    Array.prototype.forEach.call(filtro.querySelectorAll('button[data-c]'), function (b) { nombres[b.getAttribute('data-c')] = b.textContent; });
    var temas = Array.prototype.map.call(caja.querySelectorAll('.mcd-temas-lista li'), function (li, i) {
        return { i: i, x: +li.getAttribute('data-x'), y: +li.getAttribute('data-y'), c: li.getAttribute('data-c'),
                 t: li.getAttribute('data-t'), ctx: li.getAttribute('data-ctx') };
    });
    var ctx2d = document.createElement('canvas').getContext('2d');
    var FUENTE = '600 12px "Source Sans 3", Arial, sans-serif';
    var seleccion = 'todos', anchoPrevio = 0, geo = null;

    function el(nombre, attrs, padre) {
        var e = document.createElementNS(SVG, nombre);
        for (var k in attrs) e.setAttribute(k, attrs[k]);
        if (padre) padre.appendChild(e);
        return e;
    }

    // Orden de prioridad para las etiquetas: un tema de cada curso por turno, así todos los cursos tienen nombres
    function prioridad(lista) {
        var porCurso = {}, orden = [];
        lista.forEach(function (t) { (porCurso[t.c] = porCurso[t.c] || []).push(t); });
        Object.keys(porCurso).forEach(function (c) { porCurso[c].sort(function (a, b) { return a.t.length - b.t.length; }); });
        for (var r = 0, quedan = true; quedan; r++) {
            quedan = false;
            Object.keys(porCurso).forEach(function (c) { if (porCurso[c][r]) { orden.push(porCurso[c][r]); quedan = true; } });
        }
        return orden;
    }

    function pisa(a, cajas) {
        for (var i = 0; i < cajas.length; i++) {
            var b = cajas[i];
            if (a.x0 < b.x1 && b.x0 < a.x1 && a.y0 < b.y1 && b.y0 < a.y1) return true;
        }
        return false;
    }

    // Ubica etiquetas a la derecha, izquierda, arriba o abajo del punto, sin pisar otras ni salir del área
    function etiquetar() {
        if (!geo) return;
        geo.capa.innerHTML = '';
        var visibles = seleccion === 'todos' ? temas : temas.filter(function (t) { return t.c === seleccion; });
        var ocupadas = visibles.map(function (t) {  // al filtrar, las etiquetas pueden tapar puntos atenuados
 return { x0: t.px - 5, x1: t.px + 5, y0: t.py - 5, y1: t.py + 5, punto: t }; });
        prioridad(visibles).forEach(function (t) {
            var w = ctx2d.measureText(t.t).width, h = 16, g = 7;  // alto real de la línea, con ascendentes y descendentes
            var opciones = [
                { x: t.px + g, y: t.py + 4, a: 'start', b: { x0: t.px + g - 2, x1: t.px + g + w + 2, y0: t.py - h / 2 - 1, y1: t.py + h / 2 + 1 } },
                { x: t.px - g, y: t.py + 4, a: 'end', b: { x0: t.px - g - w - 2, x1: t.px - g + 2, y0: t.py - h / 2 - 1, y1: t.py + h / 2 + 1 } },
                { x: t.px, y: t.py - g - 2, a: 'middle', b: { x0: t.px - w / 2 - 2, x1: t.px + w / 2 + 2, y0: t.py - g - h - 1, y1: t.py - g + 1 } },
                { x: t.px, y: t.py + g + h - 2, a: 'middle', b: { x0: t.px - w / 2 - 2, x1: t.px + w / 2 + 2, y0: t.py + g - 1, y1: t.py + g + h + 1 } }
            ];
            for (var k = 0; k < opciones.length; k++) {
                var o = opciones[k], b = o.b;
                if (b.x0 < 2 || b.x1 > geo.W - 2 || b.y0 < 2 || b.y1 > geo.H - 2) continue;
                var otras = ocupadas.filter(function (q) { return q.punto !== t; });
                if (pisa(b, otras)) continue;
                ocupadas.push(b);
                var tx = el('text', { x: o.x, y: o.y, 'text-anchor': o.a, 'class': 'mcd-tem-etq', 'data-c': t.c, 'data-i': t.i }, geo.capa);
                tx.textContent = t.t;
                break;
            }
        });
    }

    function dibujar() {
        var W = grafico.clientWidth;
        if (!W || Math.abs(W - anchoPrevio) < 30) return;
        anchoPrevio = W;
        var chico = W < 576;
        var H = Math.round(chico ? W * 1.35 : Math.min(Math.max(W * 0.5, 420), 600));
        var pad = chico ? 14 : 24;
        grafico.innerHTML = '';
        var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, 'class': 'mcd-tem-svg' }, grafico);
        ctx2d.font = FUENTE;
        // En pantallas angostas el mapa se gira 90°: el eje más largo del t-SNE va a lo alto
        temas.forEach(function (t) {
            var u = chico ? t.y : t.x, v = chico ? t.x : t.y;
            t.px = pad + u * (W - 2 * pad);
            t.py = pad + v * (H - 2 * pad);
        });
        var puntos = el('g', {}, svg);
        temas.forEach(function (t, k) {
            t.nodo = el('circle', { cx: t.px, cy: t.py, r: chico ? 4.5 : 5.5, 'class': 'mcd-tem-punto', 'data-c': t.c, 'data-i': t.i,
                                    style: '--d:' + Math.round(t.x * 900) + 'ms' }, puntos);
        });
        geo = { W: W, H: H, capa: el('g', { 'class': 'mcd-tem-capa' }, svg), svg: svg };
        etiquetar();
        caja.classList.add('con-grafico');
        if (window.AOS && window.AOS.refresh) window.AOS.refresh();  // el bloque cambió de alto: AOS recalcula sus disparadores
    }

    // Filtro por curso
    filtro.addEventListener('click', function (e) {
        var b = e.target.closest('button');
        if (!b) return;
        seleccion = b.getAttribute('data-c');
        Array.prototype.forEach.call(filtro.querySelectorAll('button'), function (x) { x.setAttribute('aria-pressed', x === b ? 'true' : 'false'); });
        caja.classList.toggle('filtrado', seleccion !== 'todos');
        temas.forEach(function (t) { if (t.nodo) t.nodo.classList.toggle('elegido', t.c === seleccion); });
        etiquetar();
    });

    // Detalle al pasar el puntero o tocar un punto o una etiqueta
    var tip = document.createElement('div');
    tip.className = 'mcd-rec-tip';
    caja.appendChild(tip);
    function mostrar(t) {
        temas.forEach(function (o) { o.nodo.classList.toggle('activo', o === t); });
        tip.innerHTML = '<span></span><strong class="mcd-tem-tip-t"></strong><span></span>';
        tip.children[0].textContent = nombres[t.c] || '';
        tip.children[1].textContent = t.t;
        tip.children[2].textContent = t.ctx ? 'En: ' + t.ctx : '';
        var rc = caja.getBoundingClientRect(), rp = t.nodo.getBoundingClientRect();
        tip.style.left = Math.min(Math.max(rp.left + rp.width / 2 - rc.left, 130), rc.width - 130) + 'px';
        tip.style.top = (rp.top - rc.top) + 'px';
        tip.classList.add('visible');
    }
    function soltar() {
        tip.classList.remove('visible');
        temas.forEach(function (o) { if (o.nodo) o.nodo.classList.remove('activo'); });
    }
    function apuntar(e) {
        var q = e.target.closest('[data-i]');
        if (q) { mostrar(temas[+q.getAttribute('data-i')]); return; }
        if (!geo) return;
        // Sin acertarle a un punto: el más cercano, si está a menos de 18 px
        var r = geo.svg.getBoundingClientRect(), mx = e.clientX - r.left, my = e.clientY - r.top, mejor = null, dm = 18 * 18;
        temas.forEach(function (t) { var d = (t.px - mx) * (t.px - mx) + (t.py - my) * (t.py - my); if (d < dm) { dm = d; mejor = t; } });
        if (mejor) mostrar(mejor); else if (e.pointerType !== 'touch') soltar();
    }
    grafico.addEventListener('pointermove', apuntar);
    grafico.addEventListener('pointerdown', apuntar);
    grafico.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'touch') soltar(); });
    document.addEventListener('pointerdown', function (e) { if (!grafico.contains(e.target)) soltar(); });

    function iniciar() {
        dibujar();
        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (es) {
                if (es[0].isIntersecting) {
                    caja.classList.add('visible');
                    setTimeout(function () { caja.classList.add('quieta'); }, 2300);
                    io.disconnect();
                }
            }, { threshold: 0.2 });
            io.observe(grafico);
        } else {
            caja.classList.add('visible', 'quieta');
        }
        var espera;
        window.addEventListener('resize', function () { clearTimeout(espera); espera = setTimeout(dibujar, 200); });
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(iniciar, iniciar); else iniciar();
})();
