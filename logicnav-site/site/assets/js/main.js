/* ЛоджикНав — скрипты сайта: меню, галерея, форма обращения */
(function () {
  "use strict";

  /* ---------- Мобильное меню ---------- */
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    var setOpen = function (open) {
      nav.classList.toggle("is-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.querySelector(".nav-toggle-label").textContent = open ? "Закрыть" : "Меню";
    };
    toggle.addEventListener("click", function () {
      setOpen(!nav.classList.contains("is-open"));
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        setOpen(false);
        toggle.focus();
      }
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860) setOpen(false);
    });
  }

  /* ---------- Галерея: модальное окно ---------- */
  var triggers = Array.prototype.slice.call(document.querySelectorAll("[data-lightbox]"));
  if (triggers.length) {
    var items = triggers.map(function (t) {
      return { src: t.getAttribute("data-full"), alt: t.getAttribute("data-alt") || "", caption: t.getAttribute("data-caption") || "", trigger: t };
    });

    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "Просмотр фотографий");
    box.innerHTML =
      '<div class="lb-bar">' +
        '<span class="lb-count" aria-live="polite"></span>' +
        '<div class="lb-tools">' +
          '<button type="button" class="lb-btn lb-zoom-out" aria-label="Уменьшить">−</button>' +
          '<button type="button" class="lb-btn lb-zoom-in" aria-label="Увеличить">+</button>' +
          '<button type="button" class="lb-btn lb-close" aria-label="Закрыть">Закрыть</button>' +
        '</div>' +
      '</div>' +
      '<div class="lb-stage">' +
        '<button type="button" class="lb-nav lb-prev" aria-label="Предыдущее фото">‹</button>' +
        '<img alt="" draggable="false">' +
        '<button type="button" class="lb-nav lb-next" aria-label="Следующее фото">›</button>' +
      '</div>' +
      '<p class="lb-caption"></p>';
    document.body.appendChild(box);

    var stage = box.querySelector(".lb-stage");
    var img = box.querySelector("img");
    var count = box.querySelector(".lb-count");
    var cap = box.querySelector(".lb-caption");
    var btnPrev = box.querySelector(".lb-prev");
    var btnNext = box.querySelector(".lb-next");
    var btnIn = box.querySelector(".lb-zoom-in");
    var btnOut = box.querySelector(".lb-zoom-out");
    var btnClose = box.querySelector(".lb-close");

    var index = 0, scale = 1, tx = 0, ty = 0, lastFocus = null;
    var MAX = 4;

    var apply = function () {
      img.style.transform = "translate(" + tx + "px," + ty + "px) scale(" + scale + ")";
      stage.classList.toggle("is-zoomed", scale > 1);
      btnOut.disabled = scale <= 1;
      btnIn.disabled = scale >= MAX;
      if (box.classList.contains("is-open") && document.activeElement && document.activeElement.disabled) btnClose.focus();
    };
    var clampPan = function () {
      if (scale <= 1) { tx = 0; ty = 0; return; }
      var w = img.clientWidth * scale, h = img.clientHeight * scale;
      var maxX = Math.max(0, (w - stage.clientWidth) / 2 + 40);
      var maxY = Math.max(0, (h - stage.clientHeight) / 2 + 40);
      tx = Math.max(-maxX, Math.min(maxX, tx));
      ty = Math.max(-maxY, Math.min(maxY, ty));
    };
    var setScale = function (s) {
      scale = Math.max(1, Math.min(MAX, s));
      clampPan();
      apply();
    };
    var show = function (i) {
      index = (i + items.length) % items.length;
      var it = items[index];
      img.src = it.src;
      img.alt = it.alt;
      cap.textContent = it.caption;
      count.textContent = "Фото " + (index + 1) + " из " + items.length;
      var single = items.length < 2;
      btnPrev.hidden = btnNext.hidden = single;
      scale = 1; tx = 0; ty = 0; apply();
    };
    var open = function (i) {
      lastFocus = document.activeElement;
      show(i);
      box.classList.add("is-open");
      document.body.classList.add("lb-lock");
      btnClose.focus();
    };
    var close = function () {
      box.classList.remove("is-open");
      document.body.classList.remove("lb-lock");
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    };

    triggers.forEach(function (t, i) {
      t.addEventListener("click", function (e) { e.preventDefault(); open(i); });
    });
    btnClose.addEventListener("click", close);
    btnPrev.addEventListener("click", function () { show(index - 1); });
    btnNext.addEventListener("click", function () { show(index + 1); });
    btnIn.addEventListener("click", function () { setScale(scale * 1.6); });
    btnOut.addEventListener("click", function () { setScale(scale / 1.6); });
    stage.addEventListener("click", function (e) {
      if (e.target === stage) close();
    });

    document.addEventListener("keydown", function (e) {
      if (!box.classList.contains("is-open")) return;
      if (e.key === "Escape") { e.preventDefault(); close(); return; }
      if (e.key === "ArrowLeft") { e.preventDefault(); show(index - 1); return; }
      if (e.key === "ArrowRight") { e.preventDefault(); show(index + 1); return; }
      if (e.key === "+" || e.key === "=") { setScale(scale * 1.6); return; }
      if (e.key === "-") { setScale(scale / 1.6); return; }
      if (e.key === "Tab") { /* фокус остаётся внутри окна */
        var f = Array.prototype.slice.call(box.querySelectorAll("button:not([hidden]):not([disabled])"));
        if (!f.length) return;
        var first = f[0], last = f[f.length - 1];
        if (!box.contains(document.activeElement)) { e.preventDefault(); first.focus(); }
        else if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
      }
    });

    /* Жесты: свайп (без увеличения), перетаскивание и двойной тап (с увеличением), колесо мыши */
    var pts = {}, startX = 0, startY = 0, startTx = 0, startTy = 0, moved = false, pinchDist = 0, pinchScale = 1, lastTap = 0;
    var dist = function () {
      var k = Object.keys(pts);
      if (k.length < 2) return 0;
      return Math.hypot(pts[k[0]].x - pts[k[1]].x, pts[k[0]].y - pts[k[1]].y);
    };
    stage.addEventListener("pointerdown", function (e) {
      if (e.target.closest(".lb-nav")) return;
      stage.setPointerCapture(e.pointerId);
      pts[e.pointerId] = { x: e.clientX, y: e.clientY };
      startX = e.clientX; startY = e.clientY; startTx = tx; startTy = ty; moved = false;
      if (Object.keys(pts).length === 2) { pinchDist = dist(); pinchScale = scale; }
    });
    stage.addEventListener("pointermove", function (e) {
      if (!pts[e.pointerId]) return;
      pts[e.pointerId] = { x: e.clientX, y: e.clientY };
      if (Object.keys(pts).length === 2 && pinchDist) {
        setScale(pinchScale * dist() / pinchDist);
        moved = true;
        return;
      }
      var dx = e.clientX - startX, dy = e.clientY - startY;
      if (Math.abs(dx) > 4 || Math.abs(dy) > 4) moved = true;
      if (scale > 1) {
        tx = startTx + dx; ty = startTy + dy;
        clampPan(); apply();
        stage.classList.add("is-dragging");
      }
    });
    var end = function (e) {
      if (!pts[e.pointerId]) return;
      var dx = e.clientX - startX, dy = e.clientY - startY;
      delete pts[e.pointerId];
      stage.classList.remove("is-dragging");
      if (Object.keys(pts).length < 2) pinchDist = 0;
      if (Object.keys(pts).length) return;
      if (scale === 1 && Math.abs(dx) > 50 && Math.abs(dx) > Math.abs(dy) * 1.5) {
        show(index + (dx < 0 ? 1 : -1));
        return;
      }
      if (!moved && e.target === img) {
        var now = Date.now();
        if (e.pointerType === "touch" && now - lastTap > 320) { lastTap = now; return; }
        lastTap = 0;
        setScale(scale > 1 ? 1 : 2.4);
      }
    };
    stage.addEventListener("pointerup", end);
    stage.addEventListener("pointercancel", end);
    stage.addEventListener("wheel", function (e) {
      e.preventDefault();
      setScale(scale * (e.deltaY < 0 ? 1.15 : 1 / 1.15));
    }, { passive: false });
  }

  /* ---------- Форма обращения: только письмо в почтовом приложении ---------- */
  var form = document.getElementById("contact-form");
  if (form) {
    form.noValidate = true; // Собственная проверка; без JavaScript работает штатная проверка браузера.
    var status = document.getElementById("form-status");
    var actions = document.getElementById("mail-actions");
    var fallback = document.getElementById("mail-fallback");
    var copy = document.getElementById("mail-copy");
    var preparedText = "";

    // Подставляем тему из кнопок «Запросить информацию о …».
    var params = new URLSearchParams(window.location.search);
    var topic = params.get("topic");
    var subjectField = form.elements["subject"];
    if (topic && subjectField && !subjectField.value) {
      subjectField.value = topic.slice(0, 150);
    }

    var setError = function (field, msg) {
      var wrap = field.closest(".field");
      if (!wrap) return;
      wrap.classList.toggle("has-error", !!msg);
      var out = wrap.querySelector(".error-msg");
      if (out) out.textContent = msg || "";
      if (msg) field.setAttribute("aria-invalid", "true");
      else field.removeAttribute("aria-invalid");
    };

    var validate = function () {
      var first = null;
      var f = form.elements;
      var check = function (el, msg) {
        setError(el, msg);
        if (msg && !first) first = el;
      };
      check(f["name"], f["name"].value.trim() ? "" : "Укажите имя.");
      var email = f["email"].value.trim();
      check(f["email"], !email ? "Укажите электронную почту." : (/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) ? "" : "Проверьте адрес электронной почты."));
      check(f["subject"], f["subject"].value.trim() ? "" : "Укажите тему обращения.");
      check(f["message"], f["message"].value.trim() ? "" : "Опишите задачу или вопрос.");
      check(f["consent"], f["consent"].checked ? "" : "Подтвердите согласие.");
      if (first) first.focus();
      return !first;
    };

    form.addEventListener("input", function (e) {
      if (e.target.closest && e.target.closest(".has-error")) setError(e.target, "");
    });
    form.addEventListener("change", function (e) {
      if (e.target.closest && e.target.closest(".has-error")) setError(e.target, "");
    });

    form.addEventListener("submit", function (e) {
      e.preventDefault();
      status.className = "form-status";
      status.textContent = "";
      actions.hidden = true;
      if (!validate()) return;

      var f = form.elements;
      var subject = "Запрос с сайта ЛоджикНав: " + f["subject"].value.trim();
      var parts = [
        "Запрос с сайта ООО «ЛоджикНав»",
        "",
        "Имя: " + f["name"].value.trim(),
        "Организация: " + (f["organization"].value.trim() || "не указана"),
        "Электронная почта: " + f["email"].value.trim(),
        "Телефон: " + (f["phone"].value.trim() || "не указан"),
        "Тема: " + f["subject"].value.trim(),
        "",
        "Сообщение:",
        f["message"].value.trim()
      ];
      preparedText = parts.join("\n");
      var mailto = "mailto:logicnav@verhost.ru?subject=" +
        encodeURIComponent(subject) + "&body=" + encodeURIComponent(preparedText);

      fallback.setAttribute("href", mailto);
      status.className = "form-status is-ok";
      status.textContent = "Письмо подготовлено. Если почтовая программа не открылась, воспользуйтесь кнопкой ниже. Проверьте письмо и отправьте его самостоятельно.";
      actions.hidden = false;
      // Не отправляем данные через fetch или на внешний сервер.
      window.location.href = mailto;
    });

    copy.addEventListener("click", function () {
      if (!preparedText) return;
      var ok = function () {
        status.textContent = "Текст обращения скопирован. Вставьте его в письмо на logicnav@verhost.ru и отправьте самостоятельно.";
      };
      if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(preparedText).then(ok, function () {
          status.textContent = "Не удалось скопировать текст автоматически. Вы можете скопировать заполненные поля вручную.";
        });
      } else {
        var input = document.createElement("textarea");
        input.value = preparedText;
        input.style.position = "fixed";
        input.style.left = "-9999px";
        document.body.appendChild(input);
        input.select();
        var copied = document.execCommand("copy");
        input.remove();
        if (copied) ok();
        else status.textContent = "Не удалось скопировать текст автоматически. Вы можете скопировать заполненные поля вручную.";
      }
    });
  }
})();
