# Карта правок FoodGenius-Factory (форк #11003) — Phase 0, ждёт «ОК»
Воркфлоу импортирован: `FoodGenius-Factory` (id `mpfjneAkOKghTjat`, inactive). Правки нод — только после подтверждения.

## Credentials: есть / завести
| Нужно для | Есть? |
|-----------|-------|
| Apify (HTTP TikTok/IG) | ✅ токен в .env (FREE) → завести Header Auth cred, убрать из URL |
| Google Sheets OAuth2 (raw-кэш) | ✅ есть |
| Google Drive OAuth2 (temp видео) | ✅ есть |
| Gemini (скоринг/дедуп) | ✅ `dh36tHYBei17CBTc` |
| Claude/Anthropic (живой концепт) | ✅ `Anthropic account` |
| Notion (редплан) | ✅ `GOH6jHeJP5mmYapj` + базы созданы |
| Perplexity Sonar | ✅ есть |
| ScrapeCreators | ✅ есть |
| YouTube OAuth2 (залив) | ✅ подключён в UI |
| Telegram (алерты/ревью) | ✅ есть |
| SSH (ffmpeg) | ✅ есть |
| OpenRouter | ❌ не нужен — заменяем на Gemini/Claude |
| Fal AI | ❌ не нужен, если берём Вариант B (наш Gemini Veo) |
| Upload-Post (IG/Threads) | ❌ завести позже (YouTube — нативно) |

## Правки нод (раздел 5 v2) на реальном графе
1. **HTTP Request (Apify TikTok)** → `searchQueries` RU food/fitness + хэштеги; токен Apify из URL → Header Auth. ⚠️ TikTok для RU слабый → как источник мировых форматов; RU-релевантность ниже.
2. **+ Research-блок ПЕРЕД скрейпом:** Apify Instagram (food, гео RU) + Execute Workflow → WF#1 (YouTube-тренды) + HTTP Perplexity Sonar. Continue-on-Fail = ON. Merge → «сырые идеи».
3. **AI Agent (+OpenRouter)** → разделить: **Gemini Flash** (скоринг + дедуп `topic_hash`) и **Claude** (живой концепт/сценарий). Системные промты — из `prompts/*.md`.
4. **Хранилище:** raw оставить в Sheets (кэш); редакция → **Notion** (`Content Ideas`/`Content Posts`, статусы). Добавить Notion-узел после агента.
5. **⛔ Аппрув-гейт перед видео:** концепт → Notion `Needs Review`. Видео — **отдельный Schedule-триггер**, берёт только `status=Ready` и пустой `external_post_id`. Veo не жжётся без ручного ОК.
6. **Fal Submit + HTTP poll** → **Вариант B:** переключить на наш **Gemini `veo-3.0-fast`** (HTTP + опрос внутри n8n, уже отлажено в WF#2). Fal оставляем как запасной.
7. **Limit** → `amount = MAX_ITEMS_PER_RUN` (1–3).
8. **Drive upload** → temp; `drive_file_id` в Notion; очистка после публикации.
9. **+ Publishing-хвост после Drive:** YouTube Data API (Shorts, нативный OAuth) + IG/Threads (Upload-Post позже). caption с deep-link `?start=ref_<КОД>`.
10. **+ Error/Logging:** Error Trigger → Notion `Error Logs` + Telegram-алерт; проверка `external_post_id` перед публикацией; execution-lock.

## Порядок сборки
A. Credentials (Apify Header Auth) → B. Apify TikTok RU-запросы + research-блок → C. Agent split (Gemini+Claude) + Notion → D. аппрув-гейт + отдельный видео-триггер → E. Gemini Veo вместо Fal → F. Drive + YouTube-залив → G. error/lock/атрибуция → H. IG/Threads (Upload-Post).
