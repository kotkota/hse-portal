
#!/usr/bin/env python3
"""
HSE Design System Compliance Linter v1.1
Проверяет HTML-файлы на соответствие дизайн-системе НИУ ВШЭ.

Использование:
    python3 check_hse_compliance.py <путь_к_файлу.html>
    python3 check_hse_compliance.py <путь_к_файлу.html> --json

Проверки:
    [CSS]     Отсутствие подключения hse-tokens.css / fonts.css
    [ALT]     Отсутствие атрибута alt у тегов <img>
    [QUOTES]  Прямые кавычки "..." вместо «ёлочек»
    [DASHES]  Дефис вместо тире (« - » вместо « — », «2025-2026» вместо «2025–2026»)
    [COLORS]  Запрещённые HEX-цвета (не из палитры ВШЭ)
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
    "system-ui", "-apple-system", "blinkmacsystemfont", "segoe ui", "roboto",
    "georgia", "times new roman",
    "ui-monospace", "sfmono-regular", "menlo", "monaco", "consolas",
    # Общие ключевые слова CSS
    "sans-serif", "serif", "monospace",
    "inherit", "initial", "unset", "revert",
}

# =============================================================================
# 3. Вспомогательные функции и регулярные выражения
# =============================================================================

CODE_TAGS = {"code", "pre", "kbd", "samp"}

HEX_COLOR_RE = re.compile(r'#([0-9a-fA-F]{3,8})\b')
PROPERTY_DECL_RE = re.compile(r'([\w-]+)\s*:\s*([^;{}]+?)\s*(?:;|(?=\}))')
VAR_RE = re.compile(r'var\(\s*(--[\w-]+)(?:\s*,\s*([^()]+?))?\s*\)', re.IGNORECASE)

# Типографические правила
DASH_AS_HYPHEN_RE = re.compile(r'(?<=\S)\s+-\s+(?=\S)')
YEAR_RANGE_HYPHEN_RE = re.compile(r'\b(19\d\d|20\d\d)-(19\d\d|20\d\d)\b')


def strip_css_comments(css_text: str) -> str:
    """Заменяет тело комментариев пробелами, сохраняя количество строк и смещения."""
    def replacer(match):
        return re.sub(r'[^\n]', ' ', match.group(0))
    return re.sub(r'/\*.*?\*/', replacer, css_text, flags=re.DOTALL)


def normalize_hex(raw_hex: str) -> str:
    """
    Приводит hex-код к стандартному 6-значному виду в нижнем регистре.
    Для 4- и 8-значных hex отсекает альфа-канал к базовому цвету.
    """
    h = raw_hex.lower()
    if len(h) == 4:  # #abc -> #aabbcc
        return "#" + "".join(c * 2 for c in h[1:])
    if len(h) == 5:  # #rgba -> #aabbcc (базовый цвет)
        return "#" + "".join(c * 2 for c in h[1:4])
    if len(h) == 9:  # #rrggbbaa -> #rrggbb (базовый цвет)
        return h[:7]
    return h


def extract_font_names(font_family_value: str) -> list[str]:
    """Разбирает значение font-family на отдельные имена шрифтов."""
    names = []
    for part in font_family_value.split(","):
        name = part.strip().strip("'\"").lower()
        if name:
            names.append(name)
    return names


def check_font_value(value: str) -> list[str]:
    """
    Проверяет значение свойства font-family (или family-части свойства font).
    Поддерживает CSS-переменные с фолбэками: var(--hse-..., fallback).
    """
    foreign = []
    # 1. Проверяем имена переменных (должны быть --hse-*)
    for m in VAR_RE.finditer(value):
        var_name = m.group(1).lower()
        if not var_name.startswith("--hse-"):
            foreign.append(f"var({var_name})")

    # 2. Заменяем var(...) на указанный фолбэк (или пробел), чтобы проверить и фолбэк
    def repl_var(m):
        fallback = m.group(2)
        return fallback if fallback else " "

    literal_value = VAR_RE.sub(repl_var, value).strip().strip(",")
    for font_name in extract_font_names(literal_value):
        if font_name and font_name not in HSE_ALLOWED_FONTS:
            foreign.append(font_name)

    return foreign


def extract_family_from_font_shorthand(val: str) -> str:
    """Извлекает часть шрифтового семейства из составного свойства font: ..."""
    clean = re.sub(
        r'^(?:(?:italic|oblique|small-caps|bold|bolder|lighter|\d{3}|normal)\s+)*'
        r'\d+(?:\.\d+)?(?:px|pt|em|rem|%)'
        r'(?:/\d+(?:\.\d+)?(?:px|pt|em|rem|%|[\d.]+))?\s+',
        '',
        val.strip(),
        flags=re.IGNORECASE
    )
    return clean.strip()


def check_css_declarations(css_text: str, base_line: int = 1, context: str = "блоке <style>") -> list[dict]:
    """
    Анализирует CSS-код на запрещённые цвета и посторонние шрифты.
    Возвращает список словарей: {"rule": ..., "line": ..., "detail": ...}
    с точными номерами строк каждого нарушения.
    """
    issues = []
    cleaned = strip_css_comments(css_text)
    text_to_scan = cleaned + ";"

    for decl_match in PROPERTY_DECL_RE.finditer(text_to_scan):
        prop = decl_match.group(1).lower()
        val = decl_match.group(2).strip()

        offset = decl_match.start()
        line_offset = cleaned[:offset].count('\n')
        curr_line = base_line + line_offset
        line_str = curr_line if not context.startswith("файле ") else f"{context.split(' ', 1)[1]}:{curr_line}"

        # 1. Проверка HEX-цветов
        val_no_urls = re.sub(r'url\([^)]+\)', '', val)
        for hex_match in HEX_COLOR_RE.finditer(val_no_urls):
            raw = "#" + hex_match.group(1)
            normalized = normalize_hex(raw)
            if normalized not in HSE_ALLOWED_COLORS:
                issues.append({
                    "rule": "COLORS",
                    "line": line_str,
                    "detail": f"Запрещённый цвет {raw} в {context}.",
                })

        # 2. Проверка шрифтов
        bad_fonts = []
        if prop == "font-family":
            bad_fonts = check_font_value(val)
        elif prop == "font":
            family_part = extract_family_from_font_shorthand(val)
            if family_part:
                bad_fonts = check_font_value(family_part)

        for bad_font in bad_fonts:
            issues.append({
                "rule": "FONTS",
                "line": line_str,
                "detail": f"Посторонний шрифт «{bad_font}» в {context}.",
            })

    return issues


# Функции обратной совместимости для внешних вызовов
def css_color_check(css_text: str) -> list[str]:
    issues = check_css_declarations(css_text)
    return [re.search(r'#[0-9a-fA-F]{3,8}\b', iss["detail"]).group(0) for iss in issues if iss["rule"] == "COLORS"]


def css_font_check(css_text: str) -> list[str]:
    issues = check_css_declarations(css_text)
    fonts = []
    for iss in issues:
        if iss["rule"] == "FONTS":
            m = re.search(r'«(.+?)»', iss["detail"])
            if m:
                fonts.append(m.group(1))
    return fonts


# =============================================================================
# 4. HTML-парсер для сбора данных
# =============================================================================

class HSEHtmlParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.linked_css: list[str] = []
        self.inline_styles: list[tuple[int, str]] = []  # (lineno, style)
        self.style_blocks: list[tuple[int, str]] = []   # (lineno, css)
        self.img_tags_without_alt: list[tuple[int, str]] = []
        self.quote_issues: list[tuple[int, str]] = []
        self.dash_issues: list[tuple[int, str]] = []
        self._in_style = False
        self._in_script = False
        self._code_depth = 0
        self._style_start_line = 0
        self._style_buf = []

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        lineno, _ = self.getpos()

        if tag in CODE_TAGS:
            self._code_depth += 1

        if tag == "link":
            href = attr_dict.get("href", "")
            rel = attr_dict.get("rel", "")
            clean_href = href.split("?")[0].split("#")[0]
            if "stylesheet" in rel or clean_href.endswith(".css"):
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
        if tag in CODE_TAGS and self._code_depth > 0:
            self._code_depth -= 1
        if tag == "style" and self._in_style:
            self._in_style = False
            self.style_blocks.append((self._style_start_line, "".join(self._style_buf)))
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_style or self._in_script or self._code_depth > 0:
            if self._in_style:
                self._style_buf.append(data)
            return

        lineno, _ = self.getpos()
        for offset, line in enumerate(data.splitlines()):
            line_str = line.strip()
            if not line_str:
                continue

            current_line = lineno + offset

            # 1. Проверка прямых кавычек "..."
            if '"' in line_str:
                self.quote_issues.append((current_line, line_str[:100]))

            # 2. Проверка дефиса вместо тире
            if DASH_AS_HYPHEN_RE.search(line_str):
                self.dash_issues.append((
                    current_line,
                    f'Дефис с пробелами « - » вместо длинного тире « — ». Строка: {line_str[:100]}'
                ))
            elif YEAR_RANGE_HYPHEN_RE.search(line_str):
                self.dash_issues.append((
                    current_line,
                    f'Дефис в числовом диапазоне вместо короткого тире «–». Строка: {line_str[:100]}'
                ))


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
    # [QUOTES] Проверка прямых кавычек в тексте
    # -------------------------------------------------------------------------
    for lineno, snippet in parser.quote_issues:
        issues.append({
            "rule": "QUOTES",
            "line": lineno,
            "detail": f'Прямые кавычки "..." вместо «ёлочек». Строка: {snippet}',
        })

    # -------------------------------------------------------------------------
    # [DASHES] Проверка дефисов вместо тире
    # -------------------------------------------------------------------------
    for lineno, detail in parser.dash_issues:
        issues.append({
            "rule": "DASHES",
            "line": lineno,
            "detail": detail,
        })

    # -------------------------------------------------------------------------
    # [COLORS] и [FONTS] в inline-стилях
    # -------------------------------------------------------------------------
    for lineno, style_val in parser.inline_styles:
        css_issues = check_css_declarations(style_val, base_line=lineno, context="inline-стиле")
        for iss in css_issues:
            issues.append(iss)

    # -------------------------------------------------------------------------
    # [COLORS] и [FONTS] в блоках <style>
    # -------------------------------------------------------------------------
    for block_line, css_text in parser.style_blocks:
        css_issues = check_css_declarations(css_text, base_line=block_line, context="блоке <style>")
        for iss in css_issues:
            issues.append(iss)

    # -------------------------------------------------------------------------
    # [COLORS] и [FONTS] в отдельных подключённых CSS-файлах (рядом с HTML)
    # -------------------------------------------------------------------------
    for css_href in parser.linked_css:
        if css_href.startswith(("http://", "https://", "//", "/f/")):
            continue
        clean_href = css_href.split("?")[0].split("#")[0]
        css_path = html_path.parent / clean_href
        if not css_path.exists():
            continue
        css_source = css_path.read_text(encoding="utf-8", errors="replace")
        css_issues = check_css_declarations(css_source, base_line=1, context=f"файле {css_path.name}")
        for iss in css_issues:
            issues.append(iss)

    return issues


# =============================================================================
# 6. Форматирование вывода
# =============================================================================

RULE_ICONS = {
    "CSS":    "🔗",
    "ALT":    "🖼 ",
    "QUOTES": "❝ ",
    "DASHES": "➖",
    "COLORS": "🎨",
    "FONTS":  "🔤",
}

RULE_ORDER = ["CSS", "ALT", "QUOTES", "DASHES", "COLORS", "FONTS"]


def plural_ru(n: int, one: str, few: str, many: str) -> str:
    """Склонение существительных с числительными в русском языке."""
    n_abs = abs(n)
    if n_abs % 10 == 1 and n_abs % 100 != 11:
        return one
    if 2 <= n_abs % 10 <= 4 and not (12 <= n_abs % 100 <= 14):
        return few
    return many


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
        count = len(rule_issues)
        word = f"нарушени{plural_ru(count, 'е', 'я', 'й')}"
        print(f"\n  {icon} [{rule}]  {count} {word}")
        for iss in rule_issues:
            print(f"      Строка {iss['line']}: {iss['detail']}")

    total_word = f"нарушени{plural_ru(total, 'е', 'я', 'й')}"
    print(f"\n{'='*60}")
    print(f"  Итого: {total} {total_word}")
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
