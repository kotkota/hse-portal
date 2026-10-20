// ==UserScript==
// @name         HSE: к редактору
// @namespace    https://hse.ru/
// @version      1.0.0
// @description  Кнопка «редактору» на страницах *.hse.ru, если сервер отдал заголовок X-OrgUnit.
// @author       hse-editor
// @match        *://*.hse.ru/*
// @grant        GM_xmlhttpRequest
// @grant        GM.xmlHttpRequest
// @connect      hse.ru
// @connect      *.hse.ru
// @run-at       document-idle
// @homepageURL    https://github.com/kotkota/hse-portal
// @updateURL      https://raw.githubusercontent.com/kotkota/hse-portal/master/hse-editor.user.js
// @downloadURL    https://raw.githubusercontent.com/kotkota/hse-portal/master/hse-editor.user.js
// ==/UserScript==

(() => {
  "use strict";

  // Работаем только в основном окне, игнорируем сторонние iframe
  if (window.top !== window.self) return;
  if (!/(^|\.)hse\.ru$/i.test(location.hostname)) return;

  const EDIT_URL = "https://www.hse.ru/adm/edit/edit.html?cid=22700&id=";
  let currentOverlay = null;

  function extractUnitId(headers) {
    if (!headers) return null;
    const match = headers.match(/^x-orgunit:\s*([^\r\n]+)/im);
    if (!match) return null;
    const val = match[1].trim();
    return /^\d+$/.test(val) ? val : null;
  }

  function fetchHeaders(url) {
    const cleanUrl = url.split("#")[0];

    return new Promise((resolve) => {
      const makeGM = (typeof GM_xmlhttpRequest === "function")
        ? GM_xmlhttpRequest
        : (typeof GM !== "undefined" && GM && typeof GM.xmlHttpRequest === "function" ? GM.xmlHttpRequest : null);

      if (makeGM) {
        try {
          makeGM({
            method: "HEAD",
            url: cleanUrl,
            onload: (res) => {
              if (res.status === 405) {
                // Если сервер не разрешает HEAD, пробуем GET
                makeGM({
                  method: "GET",
                  url: cleanUrl,
                  onload: (res2) => resolve(extractUnitId(res2.responseHeaders)),
                  onerror: () => resolve(null)
                });
              } else {
                resolve(extractUnitId(res.responseHeaders));
              }
            },
            onerror: () => fallbackFetch(cleanUrl).then(resolve)
          });
          return;
        } catch {
          // Если GM_xmlhttpRequest выбросил исключение, пробуем обычный fetch
        }
      }

      fallbackFetch(cleanUrl).then(resolve);
    });
  }

  function fallbackFetch(url) {
    return fetch(url, { method: "HEAD", credentials: "same-origin" })
      .then((res) => {
        const val = res.headers.get("x-orgunit");
        return val && /^\d+$/.test(val.trim()) ? val.trim() : null;
      })
      .catch(() => null);
  }

  function render(unitId) {
    if (document.getElementById("hse-editor-overlay-host")) return;

    const host = document.createElement("div");
    host.id = "hse-editor-overlay-host";
    // Shadow DOM изолирует стили кнопки от страницы и наоборот
    const root = host.attachShadow({ mode: "closed" });

    root.innerHTML = `
      <style>
        :host { all: initial; }
        .wrap {
          position: fixed; right: 16px; bottom: 16px; z-index: 2147483647;
          display: flex; align-items: center; gap: 2px;
          font: 500 13px/1 -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
          background: #0f2d69; border-radius: 999px;
          box-shadow: 0 4px 14px rgba(0,0,0,.18), 0 1px 3px rgba(0,0,0,.12);
          opacity: .85; transition: opacity .15s ease, transform .15s ease;
        }
        .wrap:hover { opacity: 1; transform: translateY(-1px); }
        a {
          color: #fff; text-decoration: none; padding: 9px 4px 9px 14px;
          display: inline-flex; align-items: center; gap: 6px; white-space: nowrap;
        }
        a:focus-visible, button:focus-visible { outline: 2px solid #8fb4ff; outline-offset: 2px; border-radius: 999px; }
        button {
          all: unset; cursor: pointer; color: #fff; opacity: .55;
          width: 26px; height: 26px; margin-right: 4px; border-radius: 50%;
          display: inline-flex; align-items: center; justify-content: center; font-size: 15px;
        }
        button:hover { opacity: 1; background: rgba(255,255,255,.12); }
        @media print { .wrap { display: none; } }
      </style>
      <div class="wrap">
        <a target="_blank" rel="noopener" title="Открыть юнит #${unitId} в редакторе" href="${EDIT_URL}${encodeURIComponent(unitId)}">
          ✎ редактору
        </a>
        <button type="button" title="Скрыть" aria-label="Скрыть">×</button>
      </div>
    `;

    root.querySelector("button").addEventListener("click", () => {
      host.remove();
      currentOverlay = null;
    });

    document.documentElement.appendChild(host);
    currentOverlay = host;
  }

  async function init() {
    if (currentOverlay) {
      currentOverlay.remove();
      currentOverlay = null;
    }
    const unitId = await fetchHeaders(location.href);
    if (unitId) {
      render(unitId);
    }
  }

  // Запуск при готовности документа
  init();

  // Поддержка переходов без перезагрузки (SPA / HTML5 history)
  let lastHref = location.href;
  const onUrlChange = () => {
    if (location.href !== lastHref) {
      lastHref = location.href;
      init();
    }
  };

  window.addEventListener("popstate", onUrlChange);
  window.addEventListener("hashchange", onUrlChange);

  const wrapHistory = (type) => {
    const orig = history[type];
    if (orig) {
      history[type] = function (...args) {
        const result = orig.apply(this, args);
        onUrlChange();
        return result;
      };
    }
  };
  wrapHistory("pushState");
  wrapHistory("replaceState");
})();
