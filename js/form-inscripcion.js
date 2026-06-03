/**
 * LICDIA UNLu — form inscripcion shared module.
 *
 * Provides:
 *   - File size validation (warns >5MB, blocks >25MB)
 *   - Total size indicator at form footer
 *   - Upload progress feedback during submit (XHR)
 *   - 120s client-side timeout
 *   - On error: ZIP fallback (download + WhatsApp link prefilled)
 *
 * Usage in HTML:
 *   <script src="/js/form-inscripcion.js" defer></script>
 *   <script>
 *     document.addEventListener('DOMContentLoaded', function() {
 *       LICDIAForm.init({
 *         formId: 'formInscripcion',
 *         submitBtnId: 'btnInscripcion',
 *         successBoxId: 'successInscripcion',
 *         errorBoxId: 'errorInscripcion',
 *         webhookUrl: 'https://n8n.impulsate.lat/webhook/licdia-inscripcion',
 *         redirectUrl: 'https://licdia.unlu.edu.ar/blockchain-dev/gracias-diplomado/index.html',
 *         origenLabel: 'Inscripcion Diplomatura Blockchain',
 *         diplomaturaLabel: 'Innovacion y Desarrollo de Aplicaciones basadas en Blockchain',
 *         whatsappPhone: '541123953895',
 *         zipPrefix: 'inscripcion-licdia-blockchain'
 *       });
 *     });
 *   </script>
 */

(function (global) {
  'use strict';

  var WARN_SIZE_MB = 5;
  var BLOCK_SIZE_MB = 25;
  var TIMEOUT_MS = 120000;
  var JSZIP_CDN = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';

  function fmtBytes(b) {
    if (b < 1024) return b + ' B';
    if (b < 1024 * 1024) return (b / 1024).toFixed(1) + ' KB';
    return (b / 1024 / 1024).toFixed(1) + ' MB';
  }

  function slug(s) {
    return (s || 'sin-nombre').toLowerCase()
      .normalize('NFD').replace(/[̀-ͯ]/g, '')
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .substring(0, 50) || 'sin-nombre';
  }

  function loadJSZip() {
    if (global.JSZip) return Promise.resolve(global.JSZip);
    return new Promise(function (resolve, reject) {
      var s = document.createElement('script');
      s.src = JSZIP_CDN;
      s.onload = function () { resolve(global.JSZip); };
      s.onerror = function () { reject(new Error('No se pudo cargar JSZip')); };
      document.head.appendChild(s);
    });
  }

  function attachSizeValidation(form, opts) {
    var fileInputs = form.querySelectorAll('input[type="file"]');
    var totalEl = ensureTotalSizeIndicator(form);

    function update() {
      var total = 0;
      var hasBlocking = false;
      fileInputs.forEach(function (input) {
        clearWarning(input);
        if (!input.files || !input.files.length) return;
        var f = input.files[0];
        total += f.size;
        var sizeMb = f.size / 1024 / 1024;
        if (sizeMb > BLOCK_SIZE_MB) {
          showWarning(input, 'block',
            'Archivo demasiado grande (' + fmtBytes(f.size) + '). Maximo ' + BLOCK_SIZE_MB + ' MB. ' +
            'Comprimi el archivo o envialo aparte por WhatsApp.');
          hasBlocking = true;
        } else if (sizeMb > WARN_SIZE_MB) {
          showWarning(input, 'warn',
            'Archivo grande (' + fmtBytes(f.size) + '). El envio puede tardar varios segundos.');
        }
      });
      totalEl.textContent = 'Tamano total adjuntos: ' + fmtBytes(total);
      totalEl.dataset.blocking = hasBlocking ? 'true' : 'false';
      // Trigger any existing updateSubmitState hook
      if (typeof global.updateSubmitState === 'function') {
        try { global.updateSubmitState(); } catch (e) {}
      }
    }

    fileInputs.forEach(function (input) {
      input.addEventListener('change', update);
    });
    update();
    return function () { return totalEl.dataset.blocking !== 'true'; };
  }

  function ensureTotalSizeIndicator(form) {
    var el = form.querySelector('.licdia-total-size');
    if (el) return el;
    el = document.createElement('div');
    el.className = 'licdia-total-size text-muted small mt-2';
    el.style.textAlign = 'right';
    var btnContainer = form.querySelector('.btn-enviar-inscripcion, button[type="submit"]');
    if (btnContainer && btnContainer.parentElement) {
      btnContainer.parentElement.insertBefore(el, btnContainer);
    } else {
      form.appendChild(el);
    }
    return el;
  }

  function clearWarning(input) {
    var w = input.parentElement && input.parentElement.querySelector('.licdia-file-warning');
    if (w) w.remove();
    if (input.classList) input.classList.remove('is-invalid', 'licdia-file-warn', 'licdia-file-block');
  }

  function showWarning(input, level, msg) {
    var box = document.createElement('div');
    box.className = 'licdia-file-warning small mt-1 ' + (level === 'block' ? 'text-danger' : 'text-warning');
    box.style.fontWeight = '500';
    box.innerHTML = (level === 'block'
      ? '<i class="fas fa-times-circle me-1"></i>'
      : '<i class="fas fa-exclamation-triangle me-1"></i>') + msg;
    if (input.parentElement) input.parentElement.appendChild(box);
    if (input.classList) {
      input.classList.add(level === 'block' ? 'licdia-file-block' : 'licdia-file-warn');
      if (level === 'block') input.classList.add('is-invalid');
    }
  }

  function attachProgressUI(form) {
    var btn = form.querySelector('button[type="submit"]');
    if (!btn) return null;
    var bar = document.createElement('div');
    bar.className = 'licdia-progress mt-3';
    bar.style.cssText = 'display:none; max-width:480px; margin-left:auto; margin-right:auto;';
    bar.innerHTML =
      '<div class="progress" style="height:24px; border-radius:12px;">' +
      '  <div class="progress-bar progress-bar-striped progress-bar-animated" role="progressbar" style="width:0%; background:var(--brand, #1C2E54);">0%</div>' +
      '</div>' +
      '<div class="licdia-progress-label text-muted small mt-2 text-center">Preparando envio...</div>';
    btn.parentElement.appendChild(bar);
    return {
      el: bar,
      show: function () { bar.style.display = 'block'; },
      hide: function () { bar.style.display = 'none'; },
      update: function (pct, label) {
        var pb = bar.querySelector('.progress-bar');
        pb.style.width = pct + '%';
        pb.textContent = pct + '%';
        if (label) bar.querySelector('.licdia-progress-label').textContent = label;
      }
    };
  }

  function buildErrorUI(form, errorBox, opts) {
    // Reemplaza el contenido del errorBox por una version mejorada con ZIP + WhatsApp
    errorBox.innerHTML = '' +
      '<div class="text-center">' +
      '  <i class="fas fa-exclamation-triangle fa-3x text-warning"></i>' +
      '  <p class="mt-3 fw-bold mb-2">No pudimos enviar tu inscripcion ahora mismo.</p>' +
      '  <p class="text-muted mb-3">No te preocupes — baja tu inscripcion como ZIP y mandanosla por WhatsApp. La procesamos a mano enseguida.</p>' +
      '  <div class="d-flex flex-column flex-md-row gap-2 justify-content-center align-items-center">' +
      '    <button type="button" class="btn btn-outline-primary px-4 licdia-btn-zip">' +
      '      <i class="fas fa-file-archive me-2"></i>Descargar mi inscripcion (ZIP)' +
      '    </button>' +
      '    <a href="https://api.whatsapp.com/send?phone=' + opts.whatsappPhone + '&text=' +
              encodeURIComponent('Hola, no pude enviar la inscripcion por la web y adjunto el ZIP con mis datos y documentacion.') +
              '" target="_blank" class="btn btn-success px-4">' +
      '      <i class="fab fa-whatsapp me-2"></i>Enviar por WhatsApp' +
      '    </a>' +
      '  </div>' +
      '  <p class="text-muted small mt-3 mb-0">Te avisamos por mail cuando recibamos el ZIP. Gracias por la paciencia.</p>' +
      '  <p class="licdia-zip-status small mt-2 mb-0" style="display:none;"></p>' +
      '</div>';

    var zipBtn = errorBox.querySelector('.licdia-btn-zip');
    var statusEl = errorBox.querySelector('.licdia-zip-status');
    zipBtn.addEventListener('click', function () {
      generateZip(form, opts, statusEl, zipBtn);
    });
  }

  function generateZip(form, opts, statusEl, btn) {
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Generando ZIP...';
    statusEl.style.display = 'block';
    statusEl.className = 'licdia-zip-status small mt-2 mb-0 text-muted';
    statusEl.textContent = 'Cargando libreria ZIP...';

    loadJSZip().then(function (JSZip) {
      statusEl.textContent = 'Empaquetando archivos...';
      var zip = new JSZip();

      // 1. datos.json
      var data = {};
      var formData = new FormData(form);
      formData.forEach(function (v, k) {
        if (!(v instanceof File)) {
          data[k] = v;
        }
      });
      data['Origen'] = opts.origenLabel || 'Inscripcion LICDIA';
      data['Diplomatura'] = opts.diplomaturaLabel || '';
      data['_generated_at'] = new Date().toISOString();
      zip.file('datos.json', JSON.stringify(data, null, 2));

      // 2. datos.txt human-readable
      var lines = ['LICDIA UNLu - Datos de la inscripcion', '======================================', ''];
      Object.keys(data).forEach(function (k) {
        if (k.indexOf('_') === 0) return;
        lines.push(k + ': ' + data[k]);
      });
      lines.push('', '---', 'Fecha de generacion del ZIP: ' + data._generated_at);
      lines.push('Origen: ' + (opts.origenLabel || ''));
      zip.file('datos.txt', lines.join('\n'));

      // 3. archivos adjuntos
      var fileCount = 0;
      var pending = [];
      var fileInputs = form.querySelectorAll('input[type="file"]');
      fileInputs.forEach(function (input) {
        if (input.files && input.files[0]) {
          var f = input.files[0];
          var fieldName = input.name || input.id;
          var safeFileName = fieldName + '__' + f.name;
          pending.push(
            f.arrayBuffer().then(function (buf) {
              zip.file(safeFileName, buf);
              fileCount++;
            })
          );
        }
      });

      return Promise.all(pending).then(function () {
        statusEl.textContent = 'Comprimiendo ' + fileCount + ' archivos...';
        return zip.generateAsync({ type: 'blob', compression: 'DEFLATE', compressionOptions: { level: 6 } });
      });
    }).then(function (blob) {
      // Generar nombre
      var nombre = slug(form.querySelector('#nombre') ? form.querySelector('#nombre').value : 'sin-nombre');
      var dni = (form.querySelector('#dni') && form.querySelector('#dni').value) || 'sin-dni';
      var filename = (opts.zipPrefix || 'inscripcion-licdia') + '-' + nombre + '-' + dni + '.zip';

      // Descargar
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      setTimeout(function () { URL.revokeObjectURL(url); }, 5000);

      statusEl.className = 'licdia-zip-status small mt-2 mb-0 text-success';
      statusEl.innerHTML = '<i class="fas fa-check-circle me-1"></i>ZIP descargado: <strong>' + filename + '</strong> (' + fmtBytes(blob.size) + '). Ahora mandalo por WhatsApp.';
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-file-archive me-2"></i>Descargar de nuevo';
    }).catch(function (err) {
      statusEl.className = 'licdia-zip-status small mt-2 mb-0 text-danger';
      statusEl.textContent = 'Error generando ZIP: ' + (err && err.message ? err.message : err) + '. Probá enviar por WhatsApp directamente.';
      btn.disabled = false;
      btn.innerHTML = '<i class="fas fa-file-archive me-2"></i>Reintentar';
    });
  }

  function submitWithProgress(form, opts, progress, sizeOk) {
    return new Promise(function (resolve, reject) {
      if (!sizeOk()) {
        reject(new Error('Hay archivos que superan el limite. Revisa los avisos en rojo.'));
        return;
      }

      var data = new FormData(form);
      data.forEach(function (v, k) {
        if (v instanceof File && v.size === 0) data.delete(k);
      });
      data.append('Origen', opts.origenLabel || 'Inscripcion LICDIA');
      if (opts.diplomaturaLabel) data.append('Diplomatura', opts.diplomaturaLabel);

      var xhr = new XMLHttpRequest();
      var timedOut = false;
      var timeoutId = setTimeout(function () {
        timedOut = true;
        try { xhr.abort(); } catch (e) {}
        reject(new Error('Timeout: el envio tardo mas de ' + (TIMEOUT_MS / 1000) + ' segundos.'));
      }, TIMEOUT_MS);

      xhr.upload.addEventListener('progress', function (e) {
        if (e.lengthComputable) {
          var pct = Math.round((e.loaded / e.total) * 100);
          var label = 'Subiendo archivos (' + fmtBytes(e.loaded) + ' / ' + fmtBytes(e.total) + ')...';
          progress.update(Math.min(pct, 95), label);
          if (pct >= 100) {
            progress.update(95, 'Procesando en el servidor (creando carpeta, subiendo a Drive)...');
          }
        }
      });

      xhr.onreadystatechange = function () {
        if (xhr.readyState !== 4) return;
        clearTimeout(timeoutId);
        if (timedOut) return;
        if (xhr.status >= 200 && xhr.status < 300) {
          progress.update(100, 'Envio completado. Redirigiendo...');
          resolve(xhr.responseText);
        } else {
          reject(new Error('Error HTTP ' + xhr.status + ': ' + xhr.statusText));
        }
      };
      xhr.onerror = function () {
        clearTimeout(timeoutId);
        reject(new Error('Error de red. Probable: webhook caido o sin internet.'));
      };

      xhr.open('POST', opts.webhookUrl, true);
      xhr.setRequestHeader('Accept', 'application/json');
      xhr.send(data);
    });
  }

  var LICDIAForm = {
    init: function (opts) {
      var form = document.getElementById(opts.formId);
      if (!form) {
        console.warn('[LICDIAForm] form not found:', opts.formId);
        return;
      }
      var errorBox = opts.errorBoxId ? document.getElementById(opts.errorBoxId) : null;
      var btn = opts.submitBtnId ? document.getElementById(opts.submitBtnId) : form.querySelector('button[type="submit"]');

      // 1. Validacion de tamano
      var sizeOk = attachSizeValidation(form, opts);

      // 2. Progress UI
      var progress = attachProgressUI(form);

      // 3. Reemplazar error UI con la mejorada (ZIP + WhatsApp)
      if (errorBox) {
        buildErrorUI(form, errorBox, opts);
      }

      // 4. Override submit handler
      form.addEventListener('submit', function (e) {
        e.preventDefault();
        if (errorBox) errorBox.style.display = 'none';

        // Reservar el handler existente si hay validacion custom (campos faltantes)
        if (typeof global.getFaltantes === 'function') {
          var faltantes = global.getFaltantes();
          if (faltantes && faltantes.length > 0) {
            if (typeof global.updateSubmitState === 'function') global.updateSubmitState();
            return;
          }
        }

        if (btn) {
          btn.disabled = true;
          btn.dataset.originalHtml = btn.innerHTML;
          btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando inscripcion...';
        }
        if (progress) progress.show();

        submitWithProgress(form, opts, progress, sizeOk).then(function () {
          if (opts.redirectUrl) {
            window.location.href = opts.redirectUrl;
          } else if (opts.successBoxId) {
            var sb = document.getElementById(opts.successBoxId);
            if (sb) sb.style.display = 'block';
            form.style.display = 'none';
          }
        }).catch(function (err) {
          console.warn('[LICDIAForm] submit error:', err);
          if (progress) progress.hide();
          if (btn) {
            btn.disabled = false;
            btn.innerHTML = btn.dataset.originalHtml || '<i class="fas fa-paper-plane me-2"></i>Enviar inscripcion';
          }
          if (errorBox) {
            errorBox.style.display = 'block';
            errorBox.scrollIntoView({ behavior: 'smooth', block: 'center' });
          }
        });
      }, true);
    }
  };

  global.LICDIAForm = LICDIAForm;
})(window);
