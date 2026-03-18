# Telegram-бот для учета рабочего времени

Бот для отслеживания времени прихода и ухода сотрудников с автоматической записью в Google Sheets.

## Возможности

- Отметка прихода на работу
- Отметка ухода с работы
- Просмотр своей статистики за день
- Автоматическое определение опозданий (рабочий день с 10:00)
- Автоматическая запись всех событий в Google Sheets
- Валидация: нельзя отметиться дважды, нельзя уйти без прихода

## Быстрый старт

### 1. Создание Telegram бота

1. Найдите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Придумайте имя бота (например: "Work Time Tracker")
4. Придумайте username (например: "my_work_time_bot")
5. **Сохраните токен** - он понадобится позже

### 2. Настройка Google Sheets API

#### Шаг 1: Создайте проект в Google Cloud

1. Перейдите на [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект:
   - Нажмите на название проекта вверху
   - Нажмите "NEW PROJECT"
   - Введите название (например: "Work Time Bot")
   - Нажмите "CREATE"

#### Шаг 2: Включите Google Sheets API

1. В боковом меню выберите **APIs & Services** → **Library**
2. Найдите "Google Sheets API"
3. Нажмите на него и нажмите **ENABLE**
4. Повторите для "Google Drive API"

#### Шаг 3: Создайте сервисный аккаунт

1. Перейдите в **APIs & Services** → **Credentials**
2. Нажмите **CREATE CREDENTIALS** → **Service Account**
3. Заполните:
   - Service account name: "work-time-bot"
   - Нажмите **CREATE AND CONTINUE**
   - Role: выберите "Editor"
   - Нажмите **CONTINUE** → **DONE**

#### Шаг 4: Создайте ключ (credentials.json)

1. В списке сервисных аккаунтов найдите только что созданный
2. Нажмите на него
3. Перейдите на вкладку **KEYS**
4. Нажмите **ADD KEY** → **Create new key**
5. Выберите **JSON**
6. Нажмите **CREATE**
7. Файл `credentials.json` автоматически скачается
8. **Сохраните email сервисного аккаунта** (вида `...@...iam.gserviceaccount.com`)

#### Шаг 5: Создайте Google таблицу

1. Перейдите на [Google Sheets](https://sheets.google.com)
2. Создайте новую таблицу
3. Назовите её (например: "Work Time Logs")
4. Скопируйте **ID таблицы** из URL:
   ```
   https://docs.google.com/spreadsheets/d/[ВОТ_ЭТОТ_ID]/edit
   ```
5. Нажмите кнопку **Share** (Поделиться)
6. **Добавьте email сервисного аккаунта** с правами "Editor"
7. Нажмите "Send"

### 3. Установка проекта локально

```bash
# Клонируйте или скачайте проект
git clone <your-repo-url>
cd work-time-bot

# Установите зависимости
pip install -r requirements.txt

# Скопируйте файл credentials.json в корень проекта

# Создайте файл .env
cp .env.example .env

# Отредактируйте .env:
# BOT_TOKEN=ваш_токен_от_BotFather
# SPREADSHEET_ID=id_вашей_таблицы
```

### 4. Инициализация таблицы

```bash
# Создаст листы Logs, Users, Summary с нужной структурой
python setup_sheets.py
```

### 5. Запуск бота локально (для теста)

```bash
python bot.py
```

Откройте бота в Telegram и отправьте `/start`

## Деплой на Render.com

### Шаг 1: Подготовка проекта

1. Создайте GitHub репозиторий
2. Загрузите туда все файлы **КРОМЕ** `credentials.json` и `.env`

### Шаг 2: Создание Web Service на Render

1. Перейдите на [Render.com](https://render.com/) и зарегистрируйтесь
2. Нажмите **New** → **Web Service**
3. Подключите свой GitHub репозиторий
4. Заполните настройки:
   - **Name**: work-time-bot
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
   - **Instance Type**: Free

### Шаг 3: Добавление переменных окружения

В разделе **Environment Variables** добавьте:

1. `BOT_TOKEN` = ваш токен от BotFather
2. `SPREADSHEET_ID` = ID вашей Google таблицы

### Шаг 4: Загрузка credentials.json

#### Способ 1: Через Secret Files (рекомендуется)

1. В настройках Render перейдите в **Secret Files**
2. Нажмите **Add Secret File**
3. **Filename**: `credentials.json`
4. **Contents**: скопируйте весь текст из вашего файла credentials.json
5. Нажмите **Save**

#### Способ 2: Через переменную окружения

1. Откройте credentials.json в текстовом редакторе
2. Скопируйте весь JSON
3. В Render добавьте переменную:
   - `GOOGLE_CREDENTIALS` = вставьте JSON (одной строкой)
4. Измените код в `bot.py`:
   ```python
   # Вместо:
   creds = Credentials.from_service_account_file('credentials.json', scopes=scope)

   # Используйте:
   import json
   creds_json = os.getenv('GOOGLE_CREDENTIALS')
   creds_dict = json.loads(creds_json)
   creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
   ```

### Шаг 5: Deploy

1. Нажмите **Create Web Service**
2. Render начнёт деплой (займёт 2-5 минут)
3. Дождитесь статуса "Live"

## Структура Google Sheets

### Лист: Logs
Все события записываются сюда:

| date | user_id | name | check_in | check_out | raw_timestamp | action |
|------|---------|------|----------|-----------|---------------|--------|
| 2026-03-18 | 123456 | Daniyar | 09:05:00 | | 09:05:00 | check-in |
| 2026-03-18 | 123456 | Daniyar | | 18:30:00 | 18:30:00 | check-out |

### Лист: Users
Список всех пользователей:

| user_id | name | username |
|---------|------|----------|
| 123456 | Daniyar | daniyar_user |

### Лист: Summary
Сводка с формулами для анализа:

| name | date | check_in | check_out | late | worked_hours |
|------|------|----------|-----------|------|--------------|
| Daniyar | 2026-03-18 | 09:05:00 | 18:30:00 | OK | 9:25:00 |

## Использование бота

1. Найдите бота в Telegram
2. Отправьте `/start`
3. Используйте кнопки:
   - **Я пришел** - отметить приход
   - **Я ушел** - отметить уход
   - **Моя статистика** - посмотреть свои отметки за сегодня

## Требования

- Python 3.9+
- Telegram Bot Token
- Google Cloud Project с активными API
- Google Sheets таблица

## Безопасность

- Никогда не коммитьте `credentials.json` в GitHub
- Никогда не коммитьте `.env` файл
- Используйте Secret Files в Render
- Регулярно проверяйте доступы к таблице

## Лицензия

MIT License
