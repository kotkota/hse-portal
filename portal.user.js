// ==UserScript==
// @name        Админка фикс
// @namespace   Violentmonkey Scripts
// @match       https://www.hse.ru/adm/*
// @grant       GM_addStyle
// @version     1.26
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

    const codeInsertHeadings = Array.from(document.querySelectorAll('.panel-heading')).filter(heading => {
      return heading.textContent.includes('Кодовая вставка');
    });

    codeInsertHeadings.forEach(textarea => {
        textarea.nextElementSibling.classList.add('monospaced');
    });

    const builderBlocks = document.querySelector('.__widget_builder_source_outer');
    if (builderBlocks) {
      builderBlocks.prepend( document.querySelector('.__widget_builder_fold') );
      builderBlocks.prepend( document.querySelector('.__widget_builder_maximize') );
    }

  }, 3000);

  const css = `
    @font-face {
      font-family: 'HSE Sans';
      src: url(/f/src/global/fonts/HSESans-Regular.woff2) format("woff2"), url(/f/src/global/fonts/HSESans-Regular.woff) format("woff");
      font-weight: 400;
      font-style: normal
    }
    @font-face {
      font-family: 'HSE Sans';
      src: url(/f/src/global/fonts/HSESans-SemiBold.woff2) format("woff2"), url(/f/src/global/fonts/HSESans-SemiBold.woff) format("woff");
      font-weight: 600;
      font-style: normal
    }
    @font-face {
      font-family: 'HSE Sans';
      src: url(/f/src/global/fonts/HSESans-Bold.woff2) format("woff2"), url(/f/src/global/fonts/HSESans-Bold.woff) format("woff");
      font-weight: 700;
      font-style: normal
    }
    @font-face {
      font-family: 'HSE Sans';
      src: url(/f/src/global/fonts/HSESans-Black.woff2) format("woff2"), url(/f/src/global/fonts/HSESans-Black.woff) format("woff");
      font-weight: 900;
      font-style: normal
    }
    body, td {
      font-family: 'HSE Sans', 'Helvetica Neue', tahoma, sans-serif;
      font-size: 14px;
    }
    .monospaced {font-family: monospace;}
    div {font-size: revert;}
    .__widget_wrapper textarea {field-sizing: content;}
    label, b, strong {font-weight: 600;}
    .panel-heading {
      font-size: 16px;
      padding: .5em .75em;
    }
    .cke_editable {font-size: 16px;}

    input.ui-button {
      font-family: 'HSE Sans', 'Helvetica Neue', tahoma, sans-serif;
      text-transform: uppercase;
      padding: .5em .75em;
      font-weight: 600;
      letter-spacing: .05em;
      border-radius: 5px;
    }
    .__widget_builder_source.ui-sortable {
      box-sizing: border-box;
      height: 100svh;
    }
    .__widget_builder_destination.__widget_builder_preview.__widget_builder_destination_only {
      height: revert;
      min-height: 40px;
    }
      
    .__widget_builder_source_outer {
      position: sticky;
      top: 0;
    }
    .__widget_builder_source_outer + .__widget_builder_destination {height: 100svh;}
  `;

  GM_addStyle(css);
})();
