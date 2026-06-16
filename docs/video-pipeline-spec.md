# Видео-конвейер FoodGenius → YouTube Shorts (спецификация)

Цель: одобренная идея (Notion) → готовый вертикальный Shorts с текстом/озвучкой/музыкой → загрузка на YouTube. Всё в n8n; рендер ffmpeg на сервере; ревью в Telegram перед заливом.

## Этапы
1. **Идея → концепт (сцены).** Берём идею со `Scored`/`Ready` из Notion → генератор сценария (есть: WF `LISppXfjrbJLkbuv`, выдаёт scenes[veo_prompt, onscreen_text, voiceover], hook, packshot, music_mood). Дёшево, без Veo.
2. **Консистентный герой (UGC).** Nano Banana (`gemini-2.5-flash-image`) рисует героя 1 раз → Veo image-to-video использует это фото в каждой сцене (один человек во всех кадрах).
3. **Veo по сценам.** Цикл по scenes → Veo (`veo-3.0-fast`) с **Wait между сценами** (квота Veo низкая, ловили 429). Опрос операции внутри n8n. Клипы складываем (Google Drive temp — credential уже есть).
4. **Сборка (ffmpeg на хосте, через SSH-ноду n8n).** Уже доказано: выжигание кириллицы + доставка. Доделать: склейка сцен + субтитры по таймингу (onscreen_text) + пекшот (лого+CTA) + озвучка (TTS) + музыка.
5. **Озвучка (TTS).** Google Cloud TTS (русский голос) или Gemini TTS.
6. **Ревью.** Готовый ролик → Telegram (есть) → ты жмёшь ОК (Notion статус Ready).
7. **Залив на YouTube.** YouTube Data API v3 `videos.insert`, вертикаль + `#Shorts`, title/description/теги из концепта. start-code в описании: `t.me/foodgenius_ai_bot?start=ref_<КОД>`.

## Что уже есть
- Концепт-генератор сцен (LISppXfjrbJLkbuv) ✅
- Veo single-clip + опрос внутри n8n (Dm1J5areiV7qiTDC) ✅
- ffmpeg на хосте + n8n SSH → выжигание текста → Telegram ✅
- Google Drive credential ✅

## Что нужно достроить / получить
- **YouTube upload = OAuth2 (НЕ API-ключ).** `videos.insert` требует OAuth2 с правом `youtube.upload`. Нужен: OAuth client в GCP (consent screen + redirect `https://solarn8n.su/rest/oauth2-credential/callback`) → credential `YouTube OAuth2` в n8n + авторизация канала. ← гейт для финального шага.
- Veo image-to-video с референсом (Nano Banana) — протестировать консистентность.
- Мультисцена-сборка ffmpeg (субтитры по таймингу + пекшот + музыка + TTS).
- TTS-голос (выбрать).
- Музыка (трек/источник).
- Veo-квота: ролик = 4-5 клипов; знать дневной лимит, ставить Wait.

## Порядок сборки (предлагаемый)
A. Концепт → сцены (готово, обкатать на одной идее).
B. Мультисцена-сборка ffmpeg на тестовых/одном Veo-клипе (text+music+TTS) — без новых доступов.
C. Veo-цикл по сценам + Nano Banana герой (Veo-квота).
D. YouTube OAuth + залив (нужен OAuth от тебя).
E. Связать в один оркестратор: идея(Ready) → концепт → Veo → сборка → ревью → YouTube.
