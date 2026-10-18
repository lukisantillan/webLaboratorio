/* Maestría en Ciencia de Datos: nube de "La maestría en cuarenta términos".
   Toma la lista que genera tools/maestria/terminos.py (data-p = peso TF-IDF normalizado, data-c = curso,
   0 = varios) y la dibuja con una disposición en espiral desde el centro, como las nubes de palabras clásicas.
   La lista queda en el HTML para lectores de pantalla y buscadores; la nube es solo visual. */
(function () {
    var bloque = document.querySelector('.mcd-terminos');
    if (!bloque) return;
    var panel = bloque.querySelector('.mcd-terminos-panel');
    var lista = bloque.querySelector('.mcd-terminos-lista');
    var nube = bloque.querySelector('.mcd-terminos-nube');
    var leyenda = bloque.querySelector('.mcd-terminos-leyenda');
    var N = lista.getAttribute('data-n');
    var FUENTE = '"Source Serif 4", Georgia, serif';
    var ctx = document.createElement('canvas').getContext('2d');
    var items = Array.prototype.map.call(lista.querySelectorAll('li'), function (li) {
        return { texto: li.textContent, p: parseFloat(li.getAttribute('data-p')), c: li.getAttribute('data-c'),
                 cursos: li.getAttribute('data-cursos'), df: li.getAttribute('data-df') };
    });
    var anchoPrevio = 0;

    // Pseudoazar con semilla fija: la nube sale igual en cada visita
    function azar(semilla) {
        return function () { semilla = (semilla * 16807) % 2147483647; return (semilla - 1) / 2147483646; };
    }

    function choca(b, puestos, pad) {
        for (var i = 0; i < puestos.length; i++) {
            var o = puestos[i];
            if (Math.abs(b.x - o.x) * 2 < b.w + o.w + pad && Math.abs(b.y - o.y) * 2 < b.h + o.h + pad) return true;
        }
        return false;
    }

    function disponer(W) {
        var chico = W < 576;
        var maxPx = Math.max(34, Math.min(104, W * 0.11)), minPx = chico ? 12 : 14, pad = chico ? 3 : 5;
        var H = Math.round(W * (chico ? 1.1 : 0.5));
        for (var intento = 0; intento < 10; intento++, H = Math.round(H * 1.1)) {
            var rnd = azar(11), puestos = [], completa = true;
            for (var k = 0; k < items.length; k++) {
                var it = items[k], px = minPx + (maxPx - minPx) * it.p;
                ctx.font = '600 ' + px + 'px ' + FUENTE;
                var w = ctx.measureText(it.texto).width, h = px * 1.02;
                var vertical = k > 0 && it.texto.length <= 14 && rnd() < 0.3;
                var b = { it: it, px: px, w: vertical ? h : w, h: vertical ? w : h, vertical: vertical };
                var t0 = rnd() * 2 * Math.PI, colocada = false;
                // Espiral de Arquímedes, achatada según la proporción del panel
                for (var s = 0; s < 9000 && !colocada; s++) {
                    var t = s * 0.1, r = t * 0.9;
                    b.x = W / 2 + r * Math.cos(t + t0) * (W / H);
                    b.y = H / 2 + r * Math.sin(t + t0);
                    if (b.x - b.w / 2 < 0 || b.x + b.w / 2 > W || b.y - b.h / 2 < 0 || b.y + b.h / 2 > H) continue;
                    if (!choca(b, puestos, pad)) { puestos.push(b); colocada = true; }
                }
                if (!colocada) { completa = false; break; }
            }
            if (completa) return { H: H, puestos: puestos };
        }
        return null;
    }

    function dibujar() {
        var W = nube.clientWidth;
        if (!W || Math.abs(W - anchoPrevio) < 30) return;
        var res = disponer(W);
        if (!res) return;
        anchoPrevio = W;
        nube.innerHTML = '';
        nube.style.height = res.H + 'px';
        res.puestos.forEach(function (b, i) {
            var span = document.createElement('span');
            span.className = 'mcd-t';
            span.textContent = b.it.texto;
            span.setAttribute('data-c', b.it.c);
            span.style.fontSize = b.px.toFixed(1) + 'px';
            span.style.left = (b.x / W * 100).toFixed(3) + '%';
            span.style.top = b.y.toFixed(1) + 'px';
            span.style.setProperty('--r', b.vertical ? '-90deg' : '0deg');
            span.style.setProperty('--i', i);
            span._dato = b.it;
            nube.appendChild(span);
        });
        bloque.classList.add('con-nube');
    }

    // Detalle al pasar el puntero (o tocar): cursos donde aparece y documentos del digesto que lo usan
    var tip = document.createElement('div');
    tip.className = 'mcd-terminos-tip';
    panel.appendChild(tip);
    function enfocar(filtro) {
        nube.classList.add('enfocada');
        Array.prototype.forEach.call(nube.children, function (s) { s.classList.toggle('activa', filtro(s)); });
    }
    function soltar() {
        nube.classList.remove('enfocada');
        tip.classList.remove('visible');
    }
    function mostrarTip(span) {
        var d = span._dato, rp = panel.getBoundingClientRect(), rs = span.getBoundingClientRect();
        tip.innerHTML = '<strong></strong><span></span><span></span>';
        tip.children[0].textContent = d.texto;
        tip.children[1].textContent = d.cursos;
        tip.children[2].textContent = d.df + ' de ' + N + ' documentos del digesto';
        tip.style.left = Math.min(Math.max(rs.left + rs.width / 2 - rp.left, 140), rp.width - 140) + 'px';
        tip.style.top = (rs.top - rp.top) + 'px';
        tip.classList.add('visible');
    }
    nube.addEventListener('pointerover', function (e) {
        var s = e.target.closest('.mcd-t');
        if (!s) return;
        enfocar(function (x) { return x === s; });
        mostrarTip(s);
    });
    nube.addEventListener('pointerleave', soltar);
    nube.addEventListener('pointerout', function (e) { if (!e.relatedTarget || !e.relatedTarget.closest('.mcd-t')) soltar(); });
    leyenda.addEventListener('pointerover', function (e) {
        var li = e.target.closest('li');
        if (!li) return;
        var c = li.getAttribute('data-c');
        enfocar(function (x) { return x.getAttribute('data-c') === c; });
    });
    leyenda.addEventListener('pointerleave', soltar);

    // Entrada: los términos aparecen del más pesado al más liviano cuando el bloque entra en pantalla
    function entrar() {
        nube.classList.add('visible');
        setTimeout(function () { nube.classList.add('quieta'); }, items.length * 35 + 900);
    }
    function iniciar() {
        dibujar();
        if ('IntersectionObserver' in window) {
            var io = new IntersectionObserver(function (es) {
                if (es[0].isIntersecting) { entrar(); io.disconnect(); }
            }, { threshold: 0.25 });
            io.observe(nube);
        } else {
            entrar();
        }
        var espera;
        window.addEventListener('resize', function () {
            clearTimeout(espera);
            espera = setTimeout(function () {
                dibujar();
                if (nube.classList.contains('visible')) nube.classList.add('quieta');
            }, 200);
        });
    }
    if (document.fonts && document.fonts.load) {
        document.fonts.load('600 40px "Source Serif 4"').then(iniciar, iniciar);
    } else {
        iniciar();
    }
})();
