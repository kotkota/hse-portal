#!/usr/bin/env python3
"""
HSE Design System Compliance Linter v1.0
Проверяет HTML-файлы на соответствие дизайн-системе НИУ ВШЭ.

Использование:
    python3 check_hse_compliance.py <путь_к_файлу.html>
    python3 check_hse_compliance.py <путь_к_файлу.html> --json

Проверки:
    [COLORS]  Запрещённые HEX-цвета (не из палитры ВШЭ)
    [QUOTES]  Прямые кавычки "..." вместо «ёлочек»
    [ALT]     Отсутствие атрибута alt у тегов <img>
    [CSS]     Отсутствие подключения hse-tokens.css / fonts.css
    [FONTS]   Посторонние (не фирменные) шрифты
"""

import sys
import re
import json
import argparse
from html.parser import HTMLParser
from pathlib import Path

# =============================================================================
# 1. Разрешённые цвета палитры ВШЭ (из hse-tokens.css v1.5.0)
# =============================================================================

HSE_ALLOWED_COLORS = {
    # Brand
    "#002d6e", "#0044b0", "#0050cf", "#3a74d0", "#8eb2ec", "#c2daff", "#f0f5ff",
    "#102d69",
    # Base
    "#0f0f14", "#ffffff",
    # Background
    "#edeff3", "#f8f9fb",
    # Gray Dusk
    "#6b7a99", "#7c89a3", "#a2a9b8", "#c0c6d1", "#f0f2f5",
    # Gray Morn
    "#d3d8e6", "#e1e4eb", "#f5f6fa",
    # System Success
    "#28c75d", "#228b45", "#096237", "#e9f9ef",
    # System Error
    "#ff564e", "#d82e2e", "#b9212e", "#ffeeed",
    # System Warning
    "#f8b73f", "#e9a21d", "#8f5714", "#fef8ec",
    # Accent Dodger
    "#27a3ff", "#008ef6", "#0065b0", "#6cb4f5", "#90c3f0", "#c3ddf4", "#ebf3fa",
    # Accent Slateblue
    "#6e73f7", "#6650ec", "#581add", "#9497ff", "#b2b6ff", "#ccceff", "#f0f0fa",
    # Accent Purple
    "#935ce5", "#6929c4", "#3b0b80", "#a37ff5", "#c2a9f9", "#d8c9fb", "#f3f0fa",
    # Accent Red
    "#f0522b", "#e03a15", "#a42f15", "#ff6c47", "#ff8d70", "#ffbead", "#ffeeea",
    # Accent Orange
    "#fa8500", "#eb6d00", "#964002", "#ff941a", "#ffb366", "#ffcc99", "#fff3e6",
    # Accent Green
    "#00b86e", "#00a35f", "#0e603d", "#49b88b", "#86d1b3", "#afe1cd", "#ebf5f1",
    # Transparent / special
    "transparent", "inherit", "currentcolor",
}

# =============================================================================
# 2. Разрешённые шрифтовые семейства
# =============================================================================

HSE_ALLOWED_FONTS = {
    # Фирменные
    "hse sans", "hse slab",
    # Системные фолбэки из hse-tokens.css
    "system-ui", "-apple-system", "segoe ui", "roboto",
    "georgia", "times new roman",
    "ui-monospace", "sfmono-regular", "menlo", "monaco", "consolas",
    # Общие ключевые слова CSS
    "sans-serif", "serif", "monospace",
    "inherit", "initial", "unset", "revert",
}

# =============================================================================
# 3. Вспомогательные функции
# =============================================================================

HEX_COLOR_RE = re.compile(r'#([0-9a-fA-F]{3,8})\b')
CSS_DECL_RE = re.compile(r':\s*([^;{}]+?)\s*(?:;|(?=\}))')
INLINE_FONT_RE = re.compile(r'font-family\s*:\s*([^;}]+)', re.IGNORECASE)
# CSS-переменные: var(--hse-...) — валидны, var(--anything-else) — подозрительны
CSS_VAR_RE = re.compile(r'var\(\s*(--[\w-]+)\s*\)', re.IGNORECASE)
# Кавычки проверяем только в тексте, без HTML-тегов/атрибутов
RUSSIAN_DOUBLE_QUOTE_RE = re.compile(r'"[^"]{1,120}"')


def normalize_hex(color: str) -> str:
    """Приводит 3-символьный hex к 6-символьному и переводит в нижний регистр."""
    color = color.lower()
    if len(color) == 4:  # #abc → #aabbcc
        color = "#" + "".join(c * 2 for c in color[1:])
    return color


def extract_font_names(font_family_value: str) -> list[str]:
    """
    Разбирает значение font-family на отдельные имена шрифтов.
    'HSE Sans', Georgia, sans-serif  →  ['hse sans', 'georgia', 'sans-serif']
    """
    names = []
    for part in font_family_value.split(","):
        name = part.strip().strip("'\"").lower()
        if name:
            names.append(name)
    return names


def css_color_check(css_text: str) -> list[str]:
    """Возвращает список запрещённых цветов, найденных в CSS-коде (только в значениях свойств)."""
    forbidden = []
    text = css_text + ";"
    for decl in CSS_DECL_RE.finditer(text):
        val = decl.group(1)
        val = re.sub(r'url\([^)]+\)', '', val)
        for match in HEX_COLOR_RE.finditer(val):
            raw = "#" + match.group(1)
            normalized = normalize_hex(raw)
            if normalized not in HSE_ALLOWED_COLORS:
                forbidden.append(raw)
    return forbidden


def css_font_check(css_text: str) -> list[str]:
    """
    Возвращает список посторонних шрифтов/токенов, найденных в CSS-коде.

    Логика для CSS-переменных:
      var(--hse-font-family-*)  → валидно, пропускаем
      var(--anything-else)      → нарушение: сторонний токен
    Для литеральных имён:
      имена из HSE_ALLOWED_FONTS → валидно
      всё остальное              → нарушение
    """
    foreign = []
    for match in INLINE_FONT_RE.finditer(css_text):
        value = match.group(1)

        # Проверяем CSS-переменные, встреченные в значении
        for var_match in CSS_VAR_RE.finditer(value):
            prop = var_match.group(1).lower()          # --hse-font-family-sans
            if not prop.startswith("--hse-"):
                foreign.append(f"var({prop})")
            # --hse-* всегда валидны — пропускаем

        # Убираем все var(...) из значения и проверяем оставшиеся литеральные имена
        literal_value = CSS_VAR_RE.sub("", value).strip().strip(",")
        for font_name in extract_font_names(literal_value):
            if font_name and font_name not in HSE_ALLOWED_FONTS:
                foreign.append(font_name)

    return foreign


# =============================================================================
# 4. HTML-парсер для сбора данных
# =============================================================================

class HSEHtmlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.errors: list[dict] = []
        self.linked_css: list[str] = []
        self.inline_styles: list[tuple[int, str]] = []  # (lineno, style)
        self.style_blocks: list[tuple[int, str]] = []   # (lineno, css)
        self.img_tags_without_alt: list[tuple[int, str]] = []
        self.quote_issues: list[tuple[int, str]] = []
        self._current_tag = None
        self._in_style = False
        self._in_script = False
        self._style_start_line = 0
        self._style_buf = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        lineno, _ = self.getpos()

        if tag == "link":
            href = attr_dict.get("href", "")
            rel = attr_dict.get("rel", "")
            if "stylesheet" in rel or href.endswith(".css"):
                self.linked_css.append(href)

        if tag == "style":
            self._in_style = True
            self._style_start_line = lineno
            self._style_buf = []

        if tag == "script":
            self._in_script = True

        if "style" in attr_dict:
            self.inline_styles.append((lineno, attr_dict["style"]))

        if tag == "img":
            attrs_str = " ".join(
                f'{k}="{v}"' if v is not None else k for k, v in attrs
            )
            if "alt" not in attr_dict:
                self.img_tags_without_alt.append((lineno, f"<img {attrs_str}>"))

    def handle_endtag(self, tag):
        if tag == "style" and self._in_style:
            self._in_style = False
            self.style_blocks.append((self._style_start_line, "".join(self._style_buf)))
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_style:
            self._style_buf.append(data)
            return
        if self._in_script:
            return

        lineno, _ = self.getpos()
        for offset, line in enumerate(data.splitlines()):
            line_str = line.strip()
            if line_str and RUSSIAN_DOUBLE_QUOTE_RE.search(line_str):
                self.quote_issues.append((lineno + offset, line_str[:100]))


# =============================================================================
# 5. Основной анализатор
# =============================================================================

def lint_file(html_path: Path) -> list[dict]:
    """
    Анализирует HTML-файл и возвращает список найденных нарушений.
    Каждое нарушение — словарь: {rule, line, detail}
    """
    source = html_path.read_text(encoding="utf-8", errors="replace")
    issues: list[dict] = []

    # --- Парсим HTML ---
    parser = HSEHtmlParser()
    parser.feed(source)

    # -------------------------------------------------------------------------
    # [CSS] Проверка подключения обязательных CSS-файлов
    # -------------------------------------------------------------------------
    linked = " ".join(parser.linked_css)
    if "hse-tokens.css" not in linked:
        issues.append({
            "rule": "CSS",
            "line": 1,
            "detail": "Не подключён hse-tokens.css (обязательный файл токенов дизайн-системы).",
        })
    if "fonts.css" not in linked:
        issues.append({
            "rule": "CSS",
            "line": 1,
            "detail": "Не подключён fonts.css (обязательный файл шрифтов ВШЭ).",
        })

    # -------------------------------------------------------------------------
    # [ALT] Проверка атрибута alt у всех <img>
    # -------------------------------------------------------------------------
    for lineno, tag_str in parser.img_tags_without_alt:
        issues.append({
            "rule": "ALT",
            "line": lineno,
            "detail": f"Тег <img> без атрибута alt: {tag_str[:80]}",
        })

    # -------------------------------------------------------------------------
    # [QUOTES] Проверка прямых кавычек в тексте (не в HTML-атрибутах и тегах)
    # -------------------------------------------------------------------------
    for lineno, snippet in parser.quote_issues:
        issues.append({
            "rule": "QUOTES",
            "line": lineno,
            "detail": f'Прямые кавычки "..." вместо «ёлочек». Строка: {snippet}',
        })

    # -------------------------------------------------------------------------
    # [COLORS] и [FONTS] в inline-стилях
    # -------------------------------------------------------------------------
    for lineno, style_val in parser.inline_styles:
        for bad_color in css_color_check(style_val):
            issues.append({
                "rule": "COLORS",
                "line": lineno,
                "detail": f"Запрещённый цвет {bad_color} в inline-стиле.",
            })
        for bad_font in css_font_check(style_val):
            issues.append({
                "rule": "FONTS",
                "line": lineno,
                "detail": f"Посторонний шрифт «{bad_font}» в inline-стиле.",
            })

    # -------------------------------------------------------------------------
    # [COLORS] и [FONTS] в блоках <style>
    # -------------------------------------------------------------------------
    for block_line, css_text in parser.style_blocks:
        # Для точного номера строки внутри блока считаем смещение
        for bad_color in css_color_check(css_text):
            # Найдём приблизительную строку внутри блока
            inner_line = 0
            for i, l in enumerate(css_text.splitlines()):
                if bad_color.lower() in l.lower() or bad_color.upper() in l:
                    inner_line = i
                    break
            issues.append({
                "rule": "COLORS",
                "line": block_line + inner_line,
                "detail": f"Запрещённый цвет {bad_color} в блоке <style>.",
            })
        for bad_font in css_font_check(css_text):
            inner_line = 0
            for i, l in enumerate(css_text.splitlines()):
                if bad_font.lower() in l.lower():
                    inner_line = i
                    break
            issues.append({
                "rule": "FONTS",
                "line": block_line + inner_line,
                "detail": f"Посторонний шрифт «{bad_font}» в блоке <style>.",
            })

    # -------------------------------------------------------------------------
    # [COLORS] и [FONTS] в отдельных подключённых CSS-файлах (рядом с HTML)
    # -------------------------------------------------------------------------
    for css_href in parser.linked_css:
        # Пропускаем внешние URL и серверные пути (/f/...)
        if css_href.startswith(("http://", "https://", "//", "/f/")):
            continue
        css_path = html_path.parent / css_href
        if not css_path.exists():
            continue
        css_source = css_path.read_text(encoding="utf-8", errors="replace")
        css_lines = css_source.splitlines()

        for bad_color in css_color_check(css_source):
            lineno = next(
                (i + 1 for i, l in enumerate(css_lines)
                 if bad_color.lower() in l.lower()),
                1,
            )
            issues.append({
                "rule": "COLORS",
                "line": f"{css_path.name}:{lineno}",
                "detail": f"Запрещённый цвет {bad_color} в файле {css_path.name}.",
            })
        for bad_font in css_font_check(css_source):
            lineno = next(
                (i + 1 for i, l in enumerate(css_lines)
                 if bad_font.lower() in l.lower()),
                1,
            )
            issues.append({
                "rule": "FONTS",
                "line": f"{css_path.name}:{lineno}",
                "detail": f"Посторонний шрифт «{bad_font}» в файле {css_path.name}.",
            })

    return issues


# =============================================================================
# 6. Форматирование вывода
# =============================================================================

RULE_ICONS = {
    "CSS":    "🔗",
    "ALT":    "🖼 ",
    "QUOTES": "❝ ",
    "COLORS": "🎨",
    "FONTS":  "🔤",
}

RULE_ORDER = ["CSS", "ALT", "QUOTES", "COLORS", "FONTS"]


def print_report(html_path: Path, issues: list[dict], use_json: bool):
    if use_json:
        print(json.dumps({"file": str(html_path), "issues": issues}, ensure_ascii=False, indent=2))
        return

    print(f"\n{'='*60}")
    print(f"  HSE Compliance Linter — {html_path.name}")
    print(f"{'='*60}")

    if not issues:
        print("  ✅  Нарушений не найдено. Файл соответствует дизайн-системе ВШЭ.")
        print(f"{'='*60}\n")
        return

    # Группируем по правилу
    by_rule: dict[str, list[dict]] = {}
    for issue in issues:
        by_rule.setdefault(issue["rule"], []).append(issue)

    total = len(issues)
    for rule in RULE_ORDER:
        if rule not in by_rule:
            continue
        icon = RULE_ICONS.get(rule, "⚠️ ")
        rule_issues = by_rule[rule]
        print(f"\n  {icon} [{rule}]  {len(rule_issues)} нарушени{'е' if len(rule_issues)==1 else 'я' if len(rule_issues) in (2,3,4) else 'й'}")
        for iss in rule_issues:
            print(f"      Строка {iss['line']}: {iss['detail']}")

    print(f"\n{'='*60}")
    print(f"  Итого: {total} нарушени{'е' if total==1 else 'я' if total in (2,3,4) else 'й'}")
    print(f"{'='*60}\n")


# =============================================================================
# 7. Точка входа
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Проверяет HTML-файл на соответствие дизайн-системе НИУ ВШЭ."
    )
    parser.add_argument("html_file", help="Путь к HTML-файлу")
    parser.add_argument(
        "--json", action="store_true", dest="use_json",
        help="Вывод в формате JSON (для CI/CD-пайплайнов)"
    )
    args = parser.parse_args()

    html_path = Path(args.html_file)
    if not html_path.exists():
        print(f"Ошибка: файл не найден — {html_path}", file=sys.stderr)
        sys.exit(2)
    if html_path.suffix.lower() not in (".html", ".htm"):
        print(f"Предупреждение: файл не является HTML-документом — {html_path}", file=sys.stderr)

    issues = lint_file(html_path)
    print_report(html_path, issues, args.use_json)

    # Код выхода: 0 — OK, 1 — есть нарушения
    sys.exit(1 if issues else 0)


if __name__ == "__main__":
    main()
