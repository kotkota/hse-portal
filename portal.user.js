// ==UserScript==
// @name        Админка фикс
// @namespace   Violentmonkey Scripts
// @match       https://www.hse.ru/adm/*
// @grant       GM_addStyle
// @version     1.2
// @author      kotkota
// @description Делает админку портала Вышки более дружелюбной.
// @run-at      document-idle
// @homepageURL    https://github.com/kotkota/hse-portal
// @updateURL      https://raw.githubusercontent.com/kotkota/hse-portal/master/portal.user.js
// @downloadURL    https://raw.githubusercontent.com/kotkota/hse-portal/master/portal.user.js
// ==/UserScript==


(function() {
  'use strict';

    function adjustTextareaRows(textareaElement) {

        const textValue = textareaElement.value;
        const numberOfNewlines = (textValue.match(/\n/g) || ['']).length;

        if (numberOfNewlines > 10) {
          textareaElement.setAttribute('rows', numberOfNewlines);
        }

    }
  setTimeout(() => {

    const textAreas = document.querySelectorAll('textarea.fullWidth');

    textAreas.forEach(textarea => {

        adjustTextareaRows(textarea);
        textarea.addEventListener('input', () => adjustTextareaRows(textarea));
    });
  }, 3000);

  const css = `
    .container > div > .__widget_wrapper > .__widget_builder_destination,
    .__widget_builder_destination.__widget_builder_preview,
    .__widget_wrapper textarea {
      height: max-content !important;
    }
    .__widget_builder_source_outer {
      position: sticky;
      top: 0;
    }
  `;

  GM_addStyle(css);
})();
