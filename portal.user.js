// ==UserScript==
// @name        Админка фикс
// @namespace   Violentmonkey Scripts
// @match       https://www.hse.ru/adm/*
// @grant       GM_addStyle
// @version     1.51
// @author      kotkota
// @description Делаем админку портала Вышки более дружелюбной.
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
  
  const urlParams = new URLSearchParams(window.location.search);
  const blockName = urlParams.get('name');

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

    document.querySelectorAll('input[size]').forEach(el => el.attributes.size.nodeValue = 60);

    if ( (blockName == 'css_styles') || (blockName == 'addition_code') ) {
      document.querySelectorAll('.__widget_wrapper:has(textarea)').forEach(el => {
        el.classList.add('monospaced');
        el.querySelector('textarea').classList.add('fullWidth');
      });
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
    .monospaced textarea {
      font-family: monospace;
      border: unset;
    }
    div {font-size: revert;}
    div.panel {margin-bottom: 5px;}
    div.panel-body {padding: 10px;}
    .__widget_wrapper textarea {field-sizing: content;}
    label, b, strong {font-weight: 600 !important;}
    div.panel-heading {
      font-size: 16px;
      padding: 10px;
    }
    div.__widget_builder_maximize, div.__widget_builder_fold {
      width: 178px;
      z-index: 1;
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
      height: 90svh !important;
    }
    div.__widget_builder_destination.wide_wrapper {
      padding-bottom: unset;
      margin-bottom: unset;
    }
    .__widget_builder_destination.__widget_builder_preview.__widget_builder_destination_only {
      height: revert !important;
      min-height: 40px;
    }
    .__widget_builder_item.__widget_builder_preview:last-child {margin-bottom: unset;}
    .__widget_builder_source_outer {
      position: sticky;
      top: 0;
    }
    .__widget_builder_source_outer + .__widget_builder_destination {height: 90svh;}
    .__widget_wrapper:has(> .__widget_inline_block > select) {
      display: flex;
      align-items: baseline;
      gap: 0.5em;
      padding: 0 5px 5px;
    }
    .__widget_clone_wrapper {position: relative;}
    .__widget_clone_title:empty {display: none;}
    input[type="text"] {padding-inline: 0.3em;}
    input.__widget_clone_add_button {margin-top: 10px;}
    .__widget_clone_remove_button {
      position: absolute;
      top: 0;
      right: 0;
    }
    td.adm_leftcol {
      width: max(180px, 15vw);
      padding-inline: 5px;
    }
    div.v_menu_level1 {
      margin: 8px 2px 2px 4px;
      font-weight: 600;
    }
    .v_menu_line, .v_menu_current {
      display: flex;
      gap: .5em;
      align-items: center;
    }
    .v_menu_bulleted_item {display: contents;}

    div.vmenu_table2 div.v_menu_current_end,
    div.vmenu_table2 div.v_menu_line,
    div.vmenu_table2 div.v_menu_current {
      padding-left: 15px;
    }
    div.__widget_builder_item {padding: unset;}
    div.__widget_builder_options {
      border: unset;
      padding-inline: 2px;
      padding-bottom: 3000px;
      margin-bottom: -3000px;
    }
    .__widget_builder_info.visible {
      display: block;
      padding-block: 0.4em;
      font-weight: 600;
    }
    div.__widget_clone_wrapper {
      border: unset;
      padding: 5px;
      margin-block: 5px;
      margin-inline: unset;
    }
    div.__widget_space_left {padding-left: 10px;}
    div[style="padding-top: 5px;"] {padding-right: 5px;}
    [style="padding-top: 8px; overflow: hidden;"] {padding-top: 2px !important;}
    div.__widget_space_top {padding-top: 5px;}
    .container > h3 + br {display: none;}
    h3 + br + div {margin: unset !important;}
    div.container {padding: unset;}
    @media (min-width:1200px) {
      div.container {width: min(100% - 20px, 1560px);}
    }
	.page-header {
		margin: unset;
		
		div[style*="250px"] {width: auto !important;}
	}
    .ou-template-menu.ou-template-uc {
	    background: repeating-linear-gradient(120deg, #ffc469, #ffb300 20px, #6c757d 20px, #6c757d 40px) !important;
    }
    .container[style*="jpg"] {
    	background: repeating-linear-gradient(120deg, #fffacf, #fffacf 80px, #edeff0 80px, #e2e9ee 160px) !important;
		padding: 20px;
		margin-left: 7px !important;
    }
  `;

  GM_addStyle(css);
})();
