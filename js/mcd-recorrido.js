/* Maestría en Ciencia de Datos: gráfico "Recorrido de la cursada".
   Lee la tabla .mcd-recorrido-tabla (horas y semanas de cada curso, en el orden del cronograma) y dibuja en SVG:
   barras de ancho = semanas y alto = horas (eje izquierdo) y la línea del avance acumulado del plan (eje derecho).
   La tabla queda en el HTML para lectores de pantalla y buscadores; el gráfico es solo visual. */
(function () {
    var caja = document.querySelector('.mcd-recorrido');
    if (!caja) return;
    var grafico = caja.querySelector('.mcd-recorrido-grafico');
    var SVG = 'http://www.w3.org/2000/svg';
    var filas = Array.prototype.map.call(caja.querySelectorAll('.mcd-recorrido-tabla tbody tr'), function (tr) {
        return { nombre: tr.querySelector('th').textContent, c: tr.getAttribute('data-c'), anio: +tr.getAttribute('data-anio'),
                 corto: tr.getAttribute('data-corto'), horas: +tr.getAttribute('data-horas'),
                 semanas: +tr.getAttribute('data-semanas') || 0, inst: tr.getAttribute('data-inst') };
    });
    var total = filas.reduce(function (a, f) { return a + f.horas; }, 0);
    var VERANO = 4, TESIS = 9;  // ancho, en semanas de dibujo, del receso de verano y del tramo de la tesis
    var anchoPrevio = 0;

    function el(nombre, attrs, padre) {
        var e = document.createElementNS(SVG, nombre);
        for (var k in attrs) e.setAttribute(k, attrs[k]);
        if (padre) padre.appendChild(e);
        return e;
    }
    function pct(x) { return (Math.round(x * 10) / 10).toString().replace('.', ',') + ' %'; }

    // Posición de cada curso en semanas: de a uno, con una semana libre entre cursos
    function ubicar() {
        var u = 0, acum = 0, previo = null;
        filas.forEach(function (f) {
            if (previo !== null) u += f.anio !== previo ? (f.anio === 2 ? VERANO : 1.5) : 1;
            f.ini = u;
            f.fin = u + (f.c === 'tesis' ? TESIS : f.semanas);
            f.antes = acum / total * 100;
            acum += f.horas;
            f.despues = acum / total * 100;
            u = f.fin;
            previo = f.anio;
        });
        return u;
    }

    function dibujar() {
        var W = grafico.clientWidth;
        if (!W || Math.abs(W - anchoPrevio) < 30) return;
        anchoPrevio = W;
        var chico = W < 576;
        var H = chico ? 250 : 320, m = { l: chico ? 30 : 42, r: chico ? 36 : 48, t: 30, b: chico ? 44 : 58 };
        var U = ubicar();
        var x = function (u) { return m.l + u / U * (W - m.l - m.r); };
        var yh = function (h) { return H - m.b - h / 100 * (H - m.t - m.b); };
        var yp = yh;  // 0-100 h y 0-100 % comparten la escala vertical
        grafico.innerHTML = '';
        var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, 'class': 'mcd-rec-svg' }, grafico);
        var defs = el('defs', {}, svg);
        var trama = el('pattern', { id: 'mcd-rec-trama', width: 6, height: 6, patternUnits: 'userSpaceOnUse', patternTransform: 'rotate(45)' }, defs);
        el('line', { x1: 0, y1: 0, x2: 0, y2: 6, 'class': 'mcd-rec-trama' }, trama);

        // Grilla y ejes
        var ejes = el('g', { 'class': 'mcd-rec-ejes' }, svg);
        [0, 25, 50, 75, 100].forEach(function (v) {
            el('line', { x1: m.l, x2: W - m.r, y1: yh(v), y2: yh(v), 'class': 'mcd-rec-grilla' }, ejes);
            el('text', { x: m.l - 8, y: yh(v) + 4, 'text-anchor': 'end', 'class': 'mcd-rec-eje-h' }, ejes).textContent = v + (v === 100 && !chico ? ' h' : '');
            el('text', { x: W - m.r + 8, y: yh(v) + 4, 'class': 'mcd-rec-eje-p' }, ejes).textContent = v + ' %';
        });

        // Tramos por año, debajo del eje
        var anios = [[1, 'Primer año', 'may–dic 2027'], [2, 'Segundo año', 'feb–oct 2028'], [3, 'Tesis', 'desde nov 2028']];
        anios.forEach(function (a) {
            var fs = filas.filter(function (f) { return f.anio === a[0]; });
            var x0 = x(fs[0].ini), x1 = x(fs[fs.length - 1].fin), yb = H - m.b + (chico ? 10 : 24);
            el('path', { d: 'M' + x0 + ',' + (yb - 4) + 'V' + yb + 'H' + x1 + 'V' + (yb - 4), 'class': 'mcd-rec-tramo' }, ejes);
            var t = el('text', { x: (x0 + x1) / 2, y: yb + 15, 'text-anchor': 'middle', 'class': 'mcd-rec-anio' }, ejes);
            t.textContent = a[1];
            if (!chico) { var s = el('tspan', { 'class': 'mcd-rec-anio-fecha' }, t); s.textContent = ' · ' + a[2]; }
        });

        // Barras: ancho = semanas, alto = horas; la tesis es un tramo rayado sin escala de horas
        var barras = el('g', {}, svg);
        filas.forEach(function (f, i) {
            var g = el('g', { 'class': 'mcd-rec-curso', 'data-c': f.c, style: '--i:' + i }, barras);
            if (f.c === 'tesis') {
                el('rect', { x: x(f.ini), y: yh(100), width: x(f.fin) - x(f.ini), height: yh(0) - yh(100), rx: 4, 'class': 'mcd-rec-tesis' }, g);
            } else {
                el('rect', { x: x(f.ini) + 1, y: yh(f.horas), width: Math.max(2, x(f.fin) - x(f.ini) - 2), height: yh(0) - yh(f.horas), rx: 3, 'class': 'mcd-rec-barra' }, g);
                if (!chico) {
                    el('text', { x: (x(f.ini) + x(f.fin)) / 2, y: H - m.b + 13, 'text-anchor': 'middle', 'class': 'mcd-rec-corto' }, g).textContent = f.corto;
                }
            }
            f.g = g;
        });

        // Línea del avance acumulado: sube durante cada curso y queda plana en las semanas libres
        var cursada = filas.filter(function (f) { return f.c !== 'tesis'; });
        var tesis = filas[filas.length - 1];
        var d = 'M' + x(0) + ',' + yp(0);
        cursada.forEach(function (f) { d += 'L' + x(f.ini) + ',' + yp(f.antes) + 'L' + x(f.fin) + ',' + yp(f.despues); });
        var linea = el('path', { d: d, 'class': 'mcd-rec-linea' }, svg);
        el('path', { d: 'M' + x(cursada[cursada.length - 1].fin) + ',' + yp(tesis.antes) + 'L' + x(tesis.ini) + ',' + yp(tesis.antes) + 'L' + x(tesis.fin) + ',' + yp(100),
                     'class': 'mcd-rec-linea-tesis' }, svg);
        var largo = linea.getTotalLength();
        linea.style.setProperty('--largo', largo);

        // Marca del fin de la cursada
        var xf = x(cursada[cursada.length - 1].fin);
        el('line', { x1: xf, x2: xf, y1: m.t - 14, y2: yh(0), 'class': 'mcd-rec-marca' }, svg);
        el('text', { x: xf - 6, y: m.t - 18, 'text-anchor': 'end', 'class': 'mcd-rec-marca-txt' }, svg).textContent =
            'Fin de la cursada: ' + pct(tesis.antes);

        // Puntos al final de cada curso, donde se ancla el detalle
        var puntos = el('g', {}, svg);
        filas.forEach(function (f) {
            f.punto = el('circle', { cx: x(f.fin), cy: yp(f.despues), r: 4, 'class': 'mcd-rec-punto' }, puntos);
        });
        caja.classList.add('con-grafico');
        if (window.AOS && window.AOS.refresh) window.AOS.refresh();  // el bloque cambió de alto: AOS recalcula sus disparadores
        caja._x = x;
        caja._svg = svg;
    }

    // Detalle al pasar el puntero o tocar: como el globo de los tableros de analítica
    var tip = document.createElement('div');
    tip.className = 'mcd-rec-tip';
    caja.appendChild(tip);
    function mostrar(f) {
        filas.forEach(function (o) { o.g.classList.toggle('activo', o === f); o.punto.classList.toggle('activo', o === f); });
        caja.classList.add('enfocado');
        var sub = f.c === 'tesis' ? 'Plazo de defensa: 36 meses desde el fin de la cursada'
                                  : f.semanas + ' semanas' + (f.inst ? ' · ' + f.inst : '');
        tip.innerHTML = '<span></span><strong></strong><span></span><span></span>';
        tip.children[0].textContent = f.nombre;
        tip.children[1].textContent = f.horas + ' h';
        tip.children[2].textContent = sub;
        tip.children[3].textContent = 'Avance del plan al terminar: ' + pct(f.despues);
        var rc = caja.getBoundingClientRect(), rp = f.punto.getBoundingClientRect();
        tip.style.left = Math.min(Math.max(rp.left + rp.width / 2 - rc.left, 120), rc.width - 120) + 'px';
        tip.style.top = (rp.top - rc.top) + 'px';
        tip.classList.add('visible');
    }
    function soltar() {
        caja.classList.remove('enfocado');
        tip.classList.remove('visible');
        filas.forEach(function (o) { if (o.g) { o.g.classList.remove('activo'); o.punto.classList.remove('activo'); } });
    }
    function apuntar(e) {
        if (!caja._svg) return;
        var r = caja._svg.getBoundingClientRect(), px = e.clientX - r.left, x = caja._x;
        var f = null;
        filas.forEach(function (o) { if (px >= x(o.ini) - 4 && px <= x(o.fin) + 4) f = o; });
        if (f) mostrar(f); else soltar();
    }
    grafico.addEventListener('pointermove', apuntar);
    grafico.addEventListener('pointerdown', apuntar);  // en pantallas táctiles, un toque sin arrastrar
    // Con el dedo, el detalle queda hasta tocar fuera del gráfico (al levantarlo el navegador emite pointerleave)
    grafico.addEventListener('pointerleave', function (e) { if (e.pointerType !== 'touch') soltar(); });
    document.addEventListener('pointerdown', function (e) { if (!grafico.contains(e.target)) soltar(); });

    function iniciar() {
        dibujar();
        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (es) {
                if (es[0].isIntersecting) { caja.classList.add('visible'); io.disconnect(); }
            }, { threshold: 0.3 });
            io.observe(grafico);
        } else {
            caja.classList.add('visible');
        }
        var espera;
        window.addEventListener('resize', function () { clearTimeout(espera); espera = setTimeout(dibujar, 200); });
    }
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(iniciar, iniciar); else iniciar();
})();
