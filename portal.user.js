// ==UserScript==
// @name        Админка фикс
// @namespace   Violentmonkey Scripts
// @match       https://www.hse.ru/adm/*
// @grant       GM_addStyle
// @version     1.25
// @author      kotkota
// @description Делает админку портала Вышки более дружелюбной.
// @run-at      document-idle
// @homepageURL    https://github.com/kotkota/hse-portal
// @updateURL      https://raw.githubusercontent.com/kotkota/hse-portal/master/portal.user.js
// @downloadURL    https://raw.githubusercontent.com/kotkota/hse-portal/master/portal.user.js
// ==/UserScript==


(function() {
  'use strict';

  const css = `
    .__widget_wrapper textarea {
      field-sizing: content;;
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
