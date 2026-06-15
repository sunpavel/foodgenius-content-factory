# Контент-завод FoodGenius (n8n)

Вирусный контент-завод под нишу питания. Цель — рост охватов и подписчиков.
Формат — вертикальное короткое видео (YouTube Shorts + Instagram Reels). Стек — Gemini (текст) + Nano Banana (картинки) + Veo (видео). Тем-базы нет, идеи генерит ИИ.

## Доступ
- n8n: `https://solarn8n.su` (Timeweb). API-ключ в `.env` (не коммитить).
- Я пушу воркфлоу через REST API n8n. Секреты площадок (Gemini и т.д.) добавляешь сам в Credentials.

## Что построено
- **WF #1 — `FoodGenius · 1 · Идея + сценарий (Gemini)`** (id `LISppXfjrbJLkbuv`, **активен, протестирован**).
  Webhook → Brief (промпт) → Gemini (gemini-2.5-flash, retry x4) → Parse. Возвращает JSON: topic, hook, scenes[visual/voiceover/onscreen], caption, hashtags, cta.
  Webhook: `POST https://solarn8n.su/webhook/foodgenius-gen`. Credential: `Gemini API key` (Header Auth, id `bTDe8ELfA3zxZPYE`).
  Исходник: `wf-1-idea-script.json`.
- **WF #2 — `FoodGenius · 2 · Veo клип`** (id `Dm1J5areiV7qiTDC`).
  Webhook → Veo start → **Wait-петля опроса операции внутри n8n** → Download → Extract. Полностью server-side. Один fast-клип проверен: video/mp4 ~2.33 MB, veo-3.0-fast.
  Gemini credential — `Gemini API key (paid)` (id `dh36tHYBei17CBTc`, проект 747100677929, paid tier). Исходник: `wf-2-veo.json`.
  Защита: узел `Started?` не даёт уйти в бесконечный опрос, если Veo вернул ошибку.

## Roadmap
1. ✅ Подключение к n8n, разбор существующего паттерна (DeepSeek+AI Agent+Notion/Sheets+Telegram).
2. ✅ WF #1: генератор идей+сценариев на Gemini — активен на сервере, протестирован. ← **докручиваем промпт**
3. ✅ WF #2: Veo — один клип генерится на сервере (self-contained, Wait-loop опрос). Дальше: генерация по всем сценам сценария.
4. ⬜ Сборка: склейка клипов + субтитры + озвучка (ffmpeg на Timeweb-сервере).
5. ⬜ Ревью-гейт: первые 10-15 роликов в Google Drive на просмотр.
6. ⬜ Автозалив: старт с YouTube Shorts (чище API, квота ~6/сутки), затем Instagram Reels.

## Честные ограничения
- **Veo** выдаёт клипы ~8 сек. Полноценный Shorts = склейка + субтитры → нужен слой сборки (ffmpeg/Creatomate).
- **YouTube** квота: загрузка 1600 единиц при дефолте 10000/сутки (~6 видео/день).
- **Instagram Reels** через Meta API требует бизнес-аккаунт и публичный URL видео.

## Слой данных (тренды, чтобы не выдумывать)
Сценарии строятся на реальных сигналах, а не «с потолка». Перед генерацией — сбор данных.
- **Gemini + Google Поиск (grounding)** — ✅ в проде. Узел `Research` ищет свежие тренды и факты, отдаёт `sources` (ссылки-источники).
- **YouTube: топ Shorts ниши** — ✅ в проде. Узлы `YT search` → `YT stats` → `YT top` тянут топ роликов ниши по просмотрам (credential `YouTube API key`, id `3zDDHequPBP5JRDI`). Модель опирается на их хуки/форматы; в выдаче поле `youtube_refs`.
- **Google Trends** — ⬜ опционально через SerpApi (free ~100/мес) или pytrends.
- **trendsee.io** — ❌ нет публичного API, для автоматизации не подходит.

## Решения (зафиксировано)
- Автозалив: **YouTube Shorts** первым (Instagram Reels — следующим).
- Сборка видео: **ffmpeg на Timeweb-сервере** → на шаге 4 понадобится **SSH-доступ** к серверу (установить/проверить ffmpeg, рендерить ролики).

## Твой следующий шаг
1. Сейчас: создать Gemini API-ключ и credential `Gemini API key` в n8n (Header Auth, `x-goog-api-key`), привязать к ноде `Gemini script`. После этого я активирую WF #1 и протестирую через webhook.
2. Позже (шаг сборки): дать SSH к Timeweb-серверу для настройки ffmpeg.
