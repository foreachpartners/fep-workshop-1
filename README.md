# fep-workshop-1

## Google Sheets интеграция

В проекте реализована интеграция с Google Sheets для работы с электронными таблицами.

### Использование скрипта Google Sheets Explorer

Скрипт `backend/bin/google_sheets_explorer.py` позволяет:

- Просматривать список файлов Google Sheets в указанной папке
- Создавать тестовые таблицы с образцами данных
- Получать информацию о папках Google Drive

#### Предварительные требования

1. Создайте проект в [Google Cloud Console](https://console.cloud.google.com/)
2. Включите Google Drive API и Google Sheets API в разделе "Библиотека API"
3. Создайте учетные данные OAuth 2.0 (тип "Настольное приложение")
4. Скачайте JSON-файл с учетными данными и поместите его в одно из стандартных мест:
   - `credentials.json` (в корне проекта)
   - `backend/credentials.json` (рекомендуемое расположение)
   - `~/.config/google/credentials.json` (общесистемное расположение)

> **Важно**: Файлы учетных данных добавлены в `.gitignore` и не должны публиковаться в репозиторий

#### Примеры использования

**Просмотр списка таблиц в папке:**

```bash
python -m backend.bin.google_sheets_explorer \
  --folder ИДЕНТИФИКАТОР_ПАПКИ
```

**Создание тестовой таблицы:**

```bash
python -m backend.bin.google_sheets_explorer \
  --folder ИДЕНТИФИКАТОР_ПАПКИ \
  --create-test
```

**Создание тестовой таблицы с указанием имени:**

```bash
python -m backend.bin.google_sheets_explorer \
  --folder ИДЕНТИФИКАТОР_ПАПКИ \
  --create-test \
  --name "Моя тестовая таблица"
```

**Явное указание пути к файлу учетных данных (если он находится в нестандартном месте):**

```bash
python -m backend.bin.google_sheets_explorer \
  --credentials /нестандартный/путь/к/credentials.json \
  --folder ИДЕНТИФИКАТОР_ПАПКИ
```

**Указание кастомного пути для хранения токенов:**

```bash
python -m backend.bin.google_sheets_explorer \
  --folder ИДЕНТИФИКАТОР_ПАПКИ \
  --token /путь/к/token.json
```

#### Как найти идентификатор папки Google Drive

Идентификатор папки можно найти в URL-адресе при открытии папки в Google Drive:

```
https://drive.google.com/drive/folders/ИДЕНТИФИКАТОР_ПАПКИ
```

#### Первый запуск и аутентификация

При первом запуске скрипт:

1. Найдет файл учетных данных в одном из стандартных мест
2. Откроет окно браузера для входа в аккаунт Google
3. Запросит разрешения для доступа к Google Drive и Sheets
4. Сохранит токен аутентификации в указанный файл (по умолчанию `~/.google_sheets_token.json`)

#### Примеры вывода

```
2023-04-21 14:32:45 - __main__ - INFO - Found credentials file at: backend/credentials.json
2023-04-21 14:32:45 - __main__ - INFO - GoogleSheetsExplorer initialized with credentials file: backend/credentials.json
2023-04-21 14:32:45 - __main__ - INFO - Token file: /home/user/.google_sheets_token.json
2023-04-21 14:32:46 - __main__ - INFO - Google Drive and Sheets services initialized successfully
2023-04-21 14:32:47 - __main__ - INFO - Folder: Моя папка с таблицами (ID: 1a2b3c4d5e6f7g8h9i)
2023-04-21 14:32:47 - __main__ - INFO - Found 3 Google Sheets files in folder 1a2b3c4d5e6f7g8h9i

2023-04-21 14:32:47 - google_sheets_explorer - INFO - Google Sheets files in folder:
2023-04-21 14:32:47 - google_sheets_explorer - INFO - 1. Бюджет 2023 (ID: abcd1234efgh5678)
2023-04-21 14:32:47 - google_sheets_explorer - INFO -    Created: 2023-01-15T10:30:00.000Z, Modified: 2023-04-20T15:45:00.000Z
2023-04-21 14:32:47 - google_sheets_explorer - INFO - 2. График проекта (ID: ijkl9012mnop3456)
2023-04-21 14:32:47 - google_sheets_explorer - INFO -    Created: 2023-02-10T09:15:00.000Z, Modified: 2023-04-18T11:20:00.000Z
2023-04-21 14:32:47 - google_sheets_explorer - INFO - 3. Контакты команды (ID: qrst7890uvwx1234)
2023-04-21 14:32:47 - google_sheets_explorer - INFO -    Created: 2023-03-05T14:00:00.000Z, Modified: 2023-04-15T16:30:00.000Z
```

### Дополнительная документация

Более подробную информацию можно найти в [документации скрипта](backend/bin/README.md).
