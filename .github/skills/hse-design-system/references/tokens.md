# HSE Design System v1.5.0 — Справочник токенов (Tokens Reference)

Официальный источник: пакет `@hse-design/tokens` (v1.5.0, `package/src/`) и документация [design-system.hse.ru/v1.5.0/src-tokens-typography](https://design-system.hse.ru/v1.5.0/src-tokens-typography).
Все токены и классы оформлены в [`assets/styles/hse-tokens.css`](../assets/styles/hse-tokens.css).

---

## 1. Базовая типографика (HSE Typography)

### 1.1. Главные принципы типографики Вышки:
1. **Оптимальный размер наборного текста — 18px** (`.hse-Text_paragraph_large`, интерлиньяж 24px).
   *Размер 16px (`.hse-Text_paragraph_small`) считается мелким и используется только в крайних случаях.*
2. **Шрифтовые пары**:
   - **Заголовки и жирные акценты (600)**: `HSE Sans`.
   - **Основной наборный текст (400)**: `HSE Sans` (интерфейсный гротеск).
   - **Лиды в промо-материалах (400)**: `HSE Slab` (брусковый шрифт). Не рекомендуется использовать в интерфейсах личных кабинетов.
3. **Длина строки**: для оптимальной читабельности длина строки должна составлять **от 40 до 80 символов**, включая пробелы (`max-width: 70ch`).
4. **Контраст заголовков и текста**:
   - В промо-материалах и на лендингах: выраженный высокий контраст (например, `.hse-Text_heading_h1` 56px или `.hse-Text_heading_h2` 42px в паре с `.hse-Text_lead_large` 32px или `.hse-Text_paragraph_large` 18px).
   - В сервисных интерфейсах: контраст снижается, чтобы не перегружать внимание.

---

### 1.2. Таблица типографических классов и стилей

| Класс в HTML | Назначение | Шрифт | Размер (px) | Вес | Интерлиньяж |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `.hse-Text_heading_h1` | Заголовок 1-го уровня | `HSE Sans` | 56px | 600 | 64px |
| `.hse-Text_heading_h2` | Заголовок 2-го уровня | `HSE Sans` | 42px | 600 | 56px |
| `.hse-Text_heading_h3` | Заголовок 3-го уровня | `HSE Sans` | 32px | 600 | 40px |
| `.hse-Text_heading_h4` | Заголовок 4-го уровня | `HSE Sans` | 24px | 600 | 32px |
| `.hse-Text_lead_large` | Промо-лид большой | `HSE Slab` | 32px | 400 | 40px |
| `.hse-Text_lead_small` | Промо-лид малый | `HSE Slab` | 24px | 400 | 32px |
| **`.hse-Text_paragraph_large`** | **Основной абзац (дефолт)** | **`HSE Sans`** | **18px** | **400** | **24px** |
| `.hse-Text_paragraph_small` | Абзац малый (вторичный) | `HSE Sans` | 16px | 400 | 24px |
| `.hse-Text_caption_x_large_regular` | Подпись XL обычная | `HSE Sans` | 20px | 400 | 28px |
| `.hse-Text_caption_x_large_bold` | Подпись XL жирная | `HSE Sans` | 20px | 600 | 28px |
| `.hse-Text_caption_large_regular` | Подпись L обычная | `HSE Sans` | 18px | 400 | 24px |
| `.hse-Text_caption_large_bold` | Подпись L жирная | `HSE Sans` | 18px | 600 | 24px |
| `.hse-Text_caption_medium_regular` | Подпись M обычная | `HSE Sans` | 16px | 400 | 20px |
| `.hse-Text_caption_medium_bold` | Подпись M жирная | `HSE Sans` | 16px | 600 | 20px |
| `.hse-Text_caption_small_regular` | Подпись S обычная | `HSE Sans` | 14px | 400 | 20px |
| `.hse-Text_caption_small_bold` | Подпись S жирная | `HSE Sans` | 14px | 600 | 20px |
| `.hse-Text_caption_x_small_regular` | Подпись XS обычная | `HSE Sans` | 12px | 400 | 16px |
| `.hse-Text_caption_x_small_bold` | Подпись XS жирная | `HSE Sans` | 12px | 600 | 16px |
| `.hse-Text_label_x_small_regular` | Пометка XS | `HSE Sans` | 12px | 400 | 12px |
| `.hse-Text_label_x_small_bold` | Пометка XS жирная | `HSE Sans` | 12px | 600 | 12px |

---

## 2. Фирменные цвета (Brand Colors)

| Токен дизайн-системы | CSS-переменная | HEX | Описание |
| :--- | :--- | :--- | :--- |
| `color_brand_dark` | `--hse-color-brand-dark` | `#002D6E` | Темно-синий, шапки, глубокий контраст |
| `color_brand_twilight` | `--hse-color-brand-twilight` | `#0044B0` | Сумеречный синий |
| `color_brand` / `color_brand_1` | `--hse-color-brand` / `--hse-color-brand-1` | `#0050CF` | Базовый синий дизайн-системы, кнопки |
| `color_brand_2` | `--hse-color-brand-2` | `#3A74D0` | Интерактивный синий 2-го уровня, Hover |
| `color_brand_3` | `--hse-color-brand-3` | `#8EB2EC` | Синий 3-го уровня |
| `color_brand_4` | `--hse-color-brand-4` | `#C2DAFF` | Светло-синий 4-го уровня |
| `color_brand_5` | `--hse-color-brand-5` | `#F0F5FF` | Пастельный синий фон подложек |
| *(Полиграфия брендбука)* | `--hse-color-brand-print-navy` | `#102D69` | Темно-синий Pantone 287 C / CMYK 100 80 0 10 |

### 2.1. Семантика и роли цветов в интерфейсах (Color Hierarchy)
1. **Заголовки и основной текст на светлом фоне**:
   - По умолчанию **всегда** цвет `--hse-color-text-primary` (`#0F0F14`).
   - Статичные заголовки секций не окрашиваются в синий цвет. Синий заголовок допустим только в качестве кликабельной ссылки (например, в превью новостей).
2. **Синий цвет — это цвет взаимодействия (Action Color)**:
   - Применяется для кнопок (`--hse-color-brand`), ссылок, активных табов, чекбоксов и индикаторов состояния.
3. **Инверсные и цветные поверхности**:
   - На тёмно-синем фоне (`--hse-color-brand-dark`) или брендовом фоне (`--hse-color-brand`) текст и заголовки оформляются белым цветом (`--hse-color-text-inverse` / `#FFFFFF`).
   - На цветных пастельных подложках (карточки, баннеры) заголовок оформляется в тон карточки (например, глубокий синий или изумрудный) либо белым при высоком контрасте.

---

## 3. Базовые цвета и поверхности

| Токен | CSS-переменная | HEX | Назначение |
| :--- | :--- | :--- | :--- |
| `color_base_black` | `--hse-color-base-black` | `#0F0F14` | Основной высококонтрастный цвет текста |
| `color_base_white` | `--hse-color-base-white` | `#FFFFFF` | Белый |
| `color_background_gray_1`| `--hse-color-background-gray-1`| `#EDEFF3` | Фоновый серый 1 |
| `color_background_gray_2`| `--hse-color-background-gray-2`| `#F8F9FB` | Фоновый серый 2 (карточки, секции) |

---

## 4. Серая шкала (Gray Dusk & Gray Morn)

### Dusk (Текст и темные элементы)
- `color_gray_dusk_1` (`--hse-color-gray-dusk-1`): `#6B7A99` (вторичный текст, подписи)
- `color_gray_dusk_2` (`--hse-color-gray-dusk-2`): `#7C89A3`
- `color_gray_dusk_3` (`--hse-color-gray-dusk-3`): `#A2A9B8`
- `color_gray_dusk_4` (`--hse-color-gray-dusk-4`): `#C0C6D1`
- `color_gray_dusk_5` (`--hse-color-gray-dusk-5`): `#F0F2F5`

### Morn (Границы и светлые разделители)
- `color_gray_morn_1` (`--hse-color-gray-morn-1`): `#D3D8E6` (бордер при наведении)
- `color_gray_morn_2` (`--hse-color-gray-morn-2`): `#E1E4EB` (стандартный бордер карточек)
- `color_gray_morn_3` (`--hse-color-gray-morn-3`): `#EDEFF3`
- `color_gray_morn_4` (`--hse-color-gray-morn-4`): `#F5F6FA`

---

## 5. Системные цвета (System Status Colors)

- **Success (Успех)**: `color_system_success`: `#28C75D` (dark: `#228B45`, deepdark: `#096237`, light: `#E9F9EF`)
- **Error (Ошибка)**: `color_system_error`: `#FF564E` (dark: `#D82E2E`, deepdark: `#B9212E`, light: `#FFEEED`)
- **Warning (Внимание)**: `color_system_warning`: `#F8B73F` (dark: `#E9A21D`, deepdark: `#8F5714`, light: `#FEF8EC`)

---

## 6. Акцентные цвета дизайн-системы

- **Dodger (Голубой)**: `#27A3FF` (dark: `#008EF6`, deepdark: `#0065B0`)
- **Slateblue (Индиго)**: `#6E73F7` (dark: `#6650EC`, deepdark: `#581ADD`)
- **Purple (Пурпурный)**: `#935CE5` (dark: `#6929C4`, deepdark: `#3B0B80`)
- **Red (Красный)**: `#F0522B` (dark: `#E03A15`, deepdark: `#A42F15`)
- **Orange (Оранжевый)**: `#FA8500` (dark: `#EB6D00`, deepdark: `#964002`)
- **Green (Зеленый)**: `#00B86E` (dark: `#00A35F`, deepdark: `#0E603D`)

---

## 7. Отступы, скругления, тени

- **Скругления**: `radius_none`: 0, `radius_small`: 4px, `radius_medium`: 8px, `radius_large`: 12px.
- **Тени**: `shadow_default`: `0 1px 2px rgba(106, 122, 152, 0.15)`, `shadow_hover`: `0 4px 24px rgba(106, 122, 152, 0.15)`.
- **Отступы**: `8px`, `12px`, `16px`, `24px`, `32px`, `40px`, `48px`, `64px`, `72px`, `96px`, `124px`.
- **Брейкпоинты**: `320px`, `375px`, `768px`, `1024px`, `1280px`, `1440px`, `1920px`.
