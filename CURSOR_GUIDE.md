# Пошаговая инструкция для работы в Cursor

## Что уже готово:
- Полный код бота с валидацией
- Интеграция с Google Sheets
- Настройка для деплоя на Render

## Что нужно сделать ДО работы в Cursor:

### 1. Создать Telegram бота (5 минут)
1. Открой Telegram -> найди @BotFather
2. Отправь `/newbot`
3. Придумай имя и username
4. **СОХРАНИ ТОКЕН** (выглядит как: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Настроить Google Sheets API (15 минут)

**2.1. Создай проект в Google Cloud:**
- Перейди: https://console.cloud.google.com/
- New Project -> назови "Work Time Bot" -> Create

**2.2. Включи API:**
- Боковое меню -> APIs & Services -> Library
- Найди "Google Sheets API" -> Enable
- Найди "Google Drive API" -> Enable

**2.3. Создай сервисный аккаунт:**
- APIs & Services -> Credentials
- Create Credentials -> Service Account
- Имя: "work-time-bot" -> Role: Editor -> Done

**2.4. Скачай ключ:**
- Нажми на созданный аккаунт
- Вкладка KEYS -> Add Key -> Create new key -> JSON
- Файл `credentials.json` скачается
- **ЗАПОМНИ EMAIL** аккаунта (вида `...@...iam.gserviceaccount.com`)

**2.5. Создай Google таблицу:**
- https://sheets.google.com -> Новая таблица
- Назови "Work Time Logs"
- **СКОПИРУЙ ID** из URL (между `/d/` и `/edit`)
- Нажми Share -> добавь email сервисного аккаунта -> Editor -> Send

---

## Работа в Cursor:

### Шаг 1: Добавь credentials.json
- Скопируй скачанный файл `credentials.json` в папку проекта
- Убедись, что он в .gitignore (уже добавлено)

### Шаг 2: Создай .env файл
```bash
# Создай файл .env со следующим содержимым:

BOT_TOKEN=твой_токен_от_BotFather
SPREADSHEET_ID=id_твоей_таблицы
```

### Шаг 3: Установи зависимости
```bash
pip install -r requirements.txt
```

### Шаг 4: Настрой таблицу
```bash
python setup_sheets.py
```

Должен появиться вывод:
```
Подключение к Google Sheets успешно!
Создан лист 'Logs'
Создан лист 'Users'
Создан лист 'Summary'
```

### Шаг 5: ТЕСТ - Запусти бота локально
```bash
python bot.py
```

Если видишь:
```
Бот запущен и подключен к Google Sheets
```
-> Всё работает!

Открой бота в Telegram -> /start -> попробуй кнопки

---

## Деплой на Render (когда всё работает):

### Шаг 1: Создай GitHub репозиторий
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/твой-username/work-time-bot.git
git push -u origin main
```

**ВАЖНО:** `credentials.json` и `.env` НЕ должны попасть в GitHub (они в .gitignore)

### Шаг 2: Зарегистрируйся на Render
- https://render.com -> Sign Up
- Подключи GitHub аккаунт

### Шаг 3: Создай Web Service
1. New -> Web Service
2. Выбери репозиторий
3. Настройки:
   - Name: work-time-bot
   - Environment: Python 3
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python bot.py`
   - Instance Type: **Free**

### Шаг 4: Добавь переменные окружения
В разделе **Environment**:
- `BOT_TOKEN` = твой токен
- `SPREADSHEET_ID` = ID таблицы

### Шаг 5: Загрузи credentials.json
В разделе **Secret Files**:
- Add Secret File
- Filename: `credentials.json`
- Contents: *вставь весь JSON из файла*
- Save

### Шаг 6: Deploy
- Create Web Service
- Жди 2-5 минут
- Статус должен стать Live

---

## Чеклист перед деплоем:

- [ ] Telegram бот создан, токен есть
- [ ] Google Cloud проект настроен
- [ ] Google Sheets API включен
- [ ] Сервисный аккаунт создан, credentials.json скачан
- [ ] Таблица создана, доступ сервисному аккаунту дан
- [ ] Бот работает локально
- [ ] GitHub репозиторий создан (без credentials.json!)
- [ ] Render.com аккаунт создан
- [ ] Переменные окружения добавлены
- [ ] Secret Files загружен

---

## Частые ошибки:

### "BOT_TOKEN not found"
-> Проверь файл .env или переменные в Render

### "Не удалось подключиться к Google Sheets"
-> Проверь:
1. credentials.json в папке проекта (или в Secret Files)
2. SPREADSHEET_ID правильный
3. Сервисному аккаунту дан доступ к таблице

### "API has not been used"
-> Включи Google Sheets API и Google Drive API в Cloud Console

### Бот не отвечает на Render
-> Проверь логи: Render Dashboard -> твой сервис -> Logs

---

## Готово!

После деплоя бот будет работать 24/7, и все сотрудники смогут отмечать приход/уход.

Открой Google таблицу -> увидишь все записи в реальном времени!
