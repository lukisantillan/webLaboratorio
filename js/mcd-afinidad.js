/* Maestría en Ciencia de Datos: dendrograma "Afinidad entre cursos".
   Lee la lista de fusiones que genera tools/maestria/afinidad.py (data-a, data-b, data-d con la numeración de scipy:
   0 a 7 los cursos, 8 en adelante los grupos) y dibuja un dendrograma horizontal en SVG.
   Las listas quedan en el HTML para lectores de pantalla y buscadores; el gráfico es solo visual. */
(function () {
    var caja = document.querySelector('.mcd-afinidad');
    if (!caja) return;
    var grafico = caja.querySelector('.mcd-afinidad-grafico');
    var SVG = 'http://www.w3.org/2000/svg';
    var cursos = Array.prototype.map.call(caja.querySelectorAll('.mcd-afinidad-cursos li'), function (li) {
        return { nombre: li.textContent, c: li.getAttribute('data-c') };
    });
    var n = cursos.length;
    var fusiones = Array.prototype.map.call(caja.querySelectorAll('.mcd-afinidad-fusiones li'), function (li, k) {
        return { id: n + k, a: +li.getAttribute('data-a'), b: +li.getAttribute('data-b'), d: +li.getAttribute('data-d') };
    });
    var nodo = {};
    cursos.forEach(function (c, i) { nodo[i] = { id: i, d: 0, hojas: [i], curso: c }; });
    fusiones.forEach(function (f) { f.hojas = nodo[f.a].hojas.concat(nodo[f.b].hojas); nodo[f.id] = f; });
    var raiz = fusiones[fusiones.length - 1];
    var anchoPrevio = 0;

    function el(nombre, attrs, padre) {
        var e = document.createElementNS(SVG, nombre);
        for (var k in attrs) e.setAttribute(k, attrs[k]);
        if (padre) padre.appendChild(e);
        return e;
    }
    function num(x) { return x.toFixed(2).replace('.', ','); }

    function dibujar() {
        var W = grafico.clientWidth;
        if (!W || Math.abs(W - anchoPrevio) < 30) return;
        anchoPrevio = W;
        var chico = W < 420, fila = chico ? 30 : 34;
        // Margen izquierdo según el nombre más largo, medido con la fuente real
        var ctx = document.createElement('canvas').getContext('2d');
        ctx.font = '600 12.5px "Source Sans 3", Arial, sans-serif';
        var etiqueta = Math.max.apply(null, cursos.map(function (c) { return ctx.measureText(c.nombre).width; }));
        var m = { l: Math.ceil(etiqueta) + 26, r: 14, t: 8, b: 34 };
        var H = m.t + n * fila + m.b;
        // Eje desde 0,2: por debajo no hay fusiones y el tramo vacío le quitaría lugar al árbol
        var d0 = 0.2, d1 = Math.ceil(raiz.d * 20) / 20 + 0.02;
        var x = function (d) { return m.l + (Math.max(d, d0) - d0) / (d1 - d0) * (W - m.l - m.r); };
        grafico.innerHTML = '';
        var svg = el('svg', { viewBox: '0 0 ' + W + ' ' + H, width: W, height: H, 'class': 'mcd-afi-svg' }, grafico);

        // Orden de las hojas: recorrido del árbol desde la raíz
        var orden = [];
        (function recorrer(id) { var f = nodo[id]; if (id < n) orden.push(id); else { recorrer(f.a); recorrer(f.b); } })(raiz.id);
        orden.forEach(function (id, i) { nodo[id].y = m.t + (i + 0.5) * fila; nodo[id].x = x(0); });
        fusiones.forEach(function (f) { f.x = x(f.d); f.y = (nodo[f.a].y + nodo[f.b].y) / 2; });

        var ejes = el('g', {}, svg);
        for (var v = d0; v <= d1 + 1e-9; v += 0.05) {
            var mayor = Math.abs(v * 10 - Math.round(v * 10)) < 1e-6;
            el('line', { x1: x(v), x2: x(v), y1: m.t, y2: H - m.b, 'class': mayor ? 'mcd-afi-grilla' : 'mcd-afi-grilla menor' }, ejes);
            if (mayor) el('text', { x: x(v), y: H - m.b + 15, 'text-anchor': 'middle', 'class': 'mcd-afi-eje' }, ejes).textContent = num(v).replace(/0$/, '');
        }
        el('text', { x: (m.l + W - m.r) / 2, y: H - 3, 'text-anchor': 'middle', 'class': 'mcd-afi-eje-titulo' }, ejes).textContent =
            'distancia coseno entre contenidos';

        // Ramas: de cada hijo, horizontal hasta la altura de la fusión y vertical entre los dos hijos
        var ramas = el('g', {}, svg);
        fusiones.forEach(function (f, k) {
            var A = nodo[f.a], B = nodo[f.b];
            f.rama = el('path', { d: 'M' + A.x + ',' + A.y + 'H' + f.x + 'V' + B.y + 'H' + B.x, 'class': 'mcd-afi-rama', style: '--k2:' + k }, ramas);
            f.rama.style.setProperty('--largo', f.rama.getTotalLength());
        });
        el('path', { d: 'M' + raiz.x + ',' + raiz.y + 'h10', 'class': 'mcd-afi-rama mcd-afi-tallo', style: '--k2:' + fusiones.length }, ramas);

        // Hojas: punto y nombre del curso, con su color
        var hojas = el('g', {}, svg);
        orden.forEach(function (id) {
            var h = nodo[id], g = el('g', { 'class': 'mcd-afi-hoja', 'data-c': h.curso.c }, hojas);
            el('rect', { x: 0, y: h.y - fila / 2, width: m.l, height: fila, 'class': 'mcd-afi-blanco' }, g);  // área de toque
            el('circle', { cx: m.l - 7, cy: h.y, r: 4.5 }, g);
            el('text', { x: m.l - 17, y: h.y + 4, 'text-anchor': 'end' }, g).textContent = h.curso.nombre;
            h.g = g;
        });

        // Nodos de fusión, donde se ancla el detalle
        var nodos = el('g', {}, svg);
        fusiones.forEach(function (f) {
            f.punto = el('circle', { cx: f.x, cy: f.y, r: 4, 'class': 'mcd-afi-nodo' }, nodos);
            el('circle', { cx: f.x, cy: f.y, r: 14, 'class': 'mcd-afi-blanco', 'data-id': f.id }, nodos);
        });
        caja.classList.add('con-grafico');
        if (window.AOS && window.AOS.refresh) window.AOS.refresh();  // el bloque cambió de alto: AOS recalcula sus disparadores
    }

    // Detalle al pasar el puntero o tocar un nodo o un curso: el grupo que se forma y a qué distancia
    var tip = document.createElement('div');
    tip.className = 'mcd-rec-tip';
    caja.appendChild(tip);
    function dentro(f, g) { return g.hojas.every(function (h) { return f.hojas.indexOf(h) >= 0; }); }
    function mostrar(f) {
        caja.classList.add('enfocado');
        fusiones.forEach(function (g) {
            g.rama.classList.toggle('activa', dentro(f, g));
            g.punto.classList.toggle('activo', g === f);
        });
        Object.keys(nodo).forEach(function (id) { if (id < n) nodo[id].g.classList.toggle('activa', f.hojas.indexOf(+id) >= 0); });
        var nombres = f.hojas.map(function (h) { return cursos[h].nombre; });
        tip.innerHTML = '<span></span><strong></strong><span></span>';
        tip.children[0].textContent = nombres.slice(0, -1).join(', ') + ' y ' + nombres[nombres.length - 1];
        tip.children[1].textContent = num(f.d);
        tip.children[2].textContent = 'distancia coseno al agruparse';
        var rc = caja.getBoundingClientRect(), rp = f.punto.getBoundingClientRect();
        tip.style.left = Math.min(Math.max(rp.left + rp.width / 2 - rc.left, 110), rc.width - 110) + 'px';
        tip.style.top = (rp.top - rc.top) + 'px';
        tip.classList.add('visible');
    }
    function soltar() {
        caja.classList.remove('enfocado');
        tip.classList.remove('visible');
        fusiones.forEach(function (g) { if (g.rama) { g.rama.classList.remove('activa'); g.punto.classList.remove('activo'); } });
        Object.keys(nodo).forEach(function (id) { if (id < n && nodo[id].g) nodo[id].g.classList.remove('activa'); });
    }
    function apuntar(e) {
        var t = e.target.closest('.mcd-afi-blanco, .mcd-afi-hoja');
        if (!t) { if (e.pointerType !== 'touch') soltar(); return; }
        if (t.hasAttribute('data-id')) { mostrar(nodo[+t.getAttribute('data-id')]); return; }
        // Un curso muestra el primer grupo que forma
        var i = cursos.map(function (c) { return c.c; }).indexOf(t.closest('.mcd-afi-hoja').getAttribute('data-c'));
        for (var k = 0; k < fusiones.length; k++) if (fusiones[k].hojas.indexOf(i) >= 0) { mostrar(fusiones[k]); return; }
    }
    grafico.addEventListener('pointerover', apuntar);
    grafico.addEventListener('pointerdown', apuntar);
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
