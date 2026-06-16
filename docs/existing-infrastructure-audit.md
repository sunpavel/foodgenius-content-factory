# Phase 0 — Аудит существующей инфраструктуры (FoodGenius контент-завод)
Дата: 2026-06-15. Кода воркфлоу не писалось. Существующее не менялось.

## 1. Среда n8n
- n8n на сервере Timeweb (`solarn8n.su` / `72.56.67.126`), Docker (`n8n-n8n-1`, образ `n8nio/n8n:latest`), порт 127.0.0.1:5678, healthy, 24/7. Watchtower авто-обновляет.
- ffmpeg 4.4.2 + шрифт DejaVuSans (кириллица) установлены на хосте, рабочая папка `/opt/foodgenius/render`. Диск 28 ГБ свободно, RAM 16 ГБ.
- Управление через публичный REST API n8n (есть API-ключ). SSH к хосту по паролю (root).

## 2. Воркфлоу в инстансе (13 шт.)
**Наши (FoodGenius), забэкаплены в `n8n-workflows/_backup/`:**
- `LISppXfjrbJLkbuv` — FoodGenius · 1 · Идея + сценарий (active)
- `Dm1J5areiV7qiTDC` — FoodGenius · 2 · Veo клип (active)
- `I0kfiOB2MeLl5wsx` — FoodGenius · 3 · Render (test) (active)

**Чужие (НЕ ТРОГАТЬ):** Parse AUTO, nikita bot, GenpostAlisaDesign, Web parse Alice Design, Tender Pipe, My workflow, AUTOPOST AlisaDesign, Autopost Solar ADV, Gen. POST Solar ADV, Parser TG Alice Designer.

## 3. Карта credentials (что РЕАЛЬНО подключено в n8n)
| Тип | Имена | Для завода |
|-----|-------|-----------|
| httpHeaderAuth | Gemini API key (paid), Gemini API key | ✅ текст/Veo/Nano Banana |
| httpQueryAuth | YouTube API key | ✅ тренды |
| telegramApi | FoodGenius review bot, Alisa Design, Solar ADV, Nikita bot | ✅ ревью-доставка |
| sshPassword | Timeweb host SSH | ✅ рендер ffmpeg |
| **notionApi** | Notion account Alice Designer, skvortsovADVnotion | ⚠️ есть интеграции, но под ДРУГИЕ воркспейсы — для FoodGenius нужен доступ к своей базе |
| **googleDriveOAuth2Api** | Google Drive account | ✅ temp-хранилище видео (Phase 2b) — уже есть! |
| anthropicApi | Anthropic account | ➕ Claude доступен в n8n (на случай, если захотим сильный текст) |
| openAiApi, deepSeekApi | несколько | не нужны заводу |
| googleSheetsOAuth2Api | несколько | опц. |
| oAuth2Api | «Solar su google nano banano», Unnamed | возможно Google/Vertex — проверить при подключении Nano Banana |

**Подтверждено рабочим:** Perplexity Sonar API-ключ валиден (тестовый вызов прошёл авторизацию и биллинг). Лежит в `.env` как `PERPLEXITY_API_KEY`.

**Чего ещё НЕТ (нужно для MVP/позже):**
- Notion: доступ интеграции к воркспейсу FoodGenius + родительская страница для создания баз (или подтверждение, что реюзаем существующий `notionApi`).
- Публикация Threads: метод не выбран — Upload-Post.com (платно) или нативный Threads API (нужен токен).
- Phase 2b: Apify (платно, отложено), автозалив YouTube/Instagram (YT Data API — есть GCP; IG — Upload-Post/community-нода).

## 4. Разбор WF#1 (переиспользуем как источник, не дублируем)
Поток: `Webhook → Brief(Set) → YT search → YT stats → YT top(Code) → Research(Gemini+google_search grounding) → Gemini script → Parse`.
- **YouTube-тренды:** YouTube Data API v3 search.list (q из Brief, type=video, videoDuration=short, order=viewCount, regionCode=RU, publishedAfter −45д) → videos.list (statistics) → топ по просмотрам.
- **Грунтинг:** Gemini `gemini-2.5-flash` с `tools:[{google_search:{}}]` → свежие факты + источники (`groundingMetadata`).
- Возвращает рекламный концепт (JSON). **Для Research-воркфлоу мозга вызываем WF#1 как суб-источник (Execute Workflow), а не копируем ноды.**

## 5. Атрибуция — анализ кода бота (`foodgenius-ai`, grammy/TS)
- `/start` обрабатывается в `bot/src/commands/start.ts`. **Захват deep-link уже есть:** `/start ref_CODE` → `code = payload.slice(4).toUpperCase()` → `saveUserData(userId, { referredBy: code })` (один раз, не перезаписывает).
- Хранилище — файловое (`bot/src/data/user-storage.ts`), есть модуль `bot/src/analytics.ts` (дневные пользователи/события) и HTTP API `bot/src/api/routes.ts`.
- **Формат ссылки завода:** `https://t.me/foodgenius_ai_bot?start=ref_<КОД>` (код → upper-case; коды делать в верхнем регистре сразу, чтобы матчилось).
- **Что добавить в бот (минимально, Phase 1/2a):** endpoint в `api/routes.ts`, отдающий счётчик пользователей по `referredBy` (всего/по коду) — чтобы Analytics-воркфлоу считал конверсию поста. Бот развёрнут отдельно (Dockerfile/railway) → n8n тянет статистику по HTTP, а не из файла.

## 6. Риски (зафиксировать до соответствующих фаз)
1. **Veo-квота (Phase 2b):** уже ловили 429 на платном тарифе при нескольких генерациях подряд → дневной лимит низкий. Ролик = 4-5 клипов. До 2b снять реальный RPD, при нужде — запрос квоты/Vertex.
2. **Instagram автозалив:** официальный Graph API требует Business + публичный URL медиа; community-нода ненадёжна. Вероятно Upload-Post (платно) или полу-ручной старт. YouTube — официально, но ~6 загрузок/сутки.
3. **UGC-липсинк (Phase 2b):** Nano Banana даёт консистентного героя, точный губ-синк под TTS Veo не вытянет → v1 = озвучка поверх кадров героя.
4. **Notion-схема:** 10 таблиц из ТЗ — для MVP избыточно; старт на 4 (см. план).

## 7. Предлагаемый MVP (ждёт «ОК», код не пишу)
**Phase 1 — Мозг** (суб-воркфлоу-оркестратор):
1. `00-content-research` — Perplexity Sonar (`sonar`, дёшево) + вызов WF#1 как источник → собрать 5-10 идей.
2. `01-topic-scoring` — `gemini-2.5-flash`, формула из ТЗ, отсев <6.
3. `02-duplicate-check` — `topic_hash` + LLM-чек против шортлиста (без эмбеддингов на старте).
4. `04-editorial-review` — запись идей/черновиков в **Notion** (статусы), ручной аппрув.
5. `06-error-logging` + защита (`MAX_ITEMS_PER_RUN`=5, execution_lock, processed-флаги).
**Notion на старте — 4 базы:** Content Ideas, Content Posts, Published Posts, Analytics (CTA Library/Hypotheses/Segments/Prompt Versions — позже).

**Phase 2a — Текст/Threads** (быстрый трафик):
6. `03-draft-generation-text` (Gemini, на основе виральных паттернов) → `product-cta-agent` (генерит `ref_<КОД>` deep-link) → `proofreader`.
7. `05-threads-publishing` — публикация утверждённого (Ready) + запись `start_code`.
8. Мелкий endpoint в боте: статистика по `referredBy` (для будущего Learning).

**Phase 2b (видео) и Phase 3 (аналитика/обучение)** — после прохождения чек-листа Phase 1+2a.

## 8. Что нужно от пользователя, чтобы стартовать Phase 1
1. **Notion:** создать интеграцию с доступом к воркспейсу FoodGenius + дать `NOTION_TOKEN` и id родительской страницы (я создам 4 базы по схеме), либо подтвердить реюз существующего `notionApi`.
2. **Threads:** выбрать метод публикации — Upload-Post.com (дать ключ) или нативный Threads API (дать токен). Нужно только к Phase 2a, Phase 1 можно начать без него.
3. **«ОК» на MVP-план** — после этого пишу первый воркфлоу (`00-content-research`).
