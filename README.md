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
4. Сохранит токен аутентификации в указанный файл (по умолчанию `~/.google_sheets_token.json` в домашней директории пользователя)

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

## Доступ к Browsable API

API проекта документировано с помощью OpenAPI (Swagger) и доступно через браузер для тестирования и изучения.

### Как получить доступ к Browsable API

1. Запустите backend-сервер:
   ```bash
   cd backend
   python -m bin.run_api
   ```

2. Откройте в браузере следующие URL для доступа к API:
   - **Swagger UI**: http://localhost:8000/docs
   - **ReDoc UI**: http://localhost:8000/redoc
   - **OpenAPI Schema**: http://localhost:8000/openapi.json

В Swagger UI вы можете интерактивно тестировать все доступные эндпоинты, отправлять запросы и просматривать ответы прямо из браузера. Это удобный инструмент для разработки и тестирования API.

### Структура API

API организовано по ресурсам и доступно по префиксу `/api`:

- `/api/projects` - управление проектами
- `/api/specialists` - управление специалистами
- `/api/periods` - управление периодами оплаты
- `/api/timesheets` - управление таймшитами
- `/api/reports` - генерация отчетов

## Настройка Google Sheets интеграции для создания проектов

Для корректной работы функции создания проектов необходимо настроить доступ к шаблонам Google Sheets. 

### Требуемые переменные окружения

В файле `.env` необходимо указать следующие переменные:

```bash
# ID папки в Google Drive для проектов
GOOGLE_PROJECTS_FOLDER_ID=your_folder_id

# ID шаблонов Google Sheets
GOOGLE_PROJECT_INFO_TEMPLATE_ID=your_info_template_id
GOOGLE_PROJECT_REPORT_TEMPLATE_ID=your_report_template_id
GOOGLE_PROJECT_CALCULATIONS_TEMPLATE_ID=your_calculations_template_id
```

### Настройка доступа к шаблонам

Для корректной работы API необходимо настроить доступ к шаблонам:

1. Откройте каждый шаблон Google Sheets в браузере
2. Нажмите на кнопку "Поделиться" (Share)
3. В разделе "Общий доступ" (General access) выберите "Доступ по ссылке" (Anyone with the link)
4. Установите уровень доступа "Просмотр" (Viewer)
5. Нажмите "Готово" (Done)

Это необходимо сделать для всех трех шаблонов, указанных в переменных окружения.

### Создание собственных шаблонов

Если вы хотите использовать собственные шаблоны:

1. Создайте новые Google Sheets документы по образцу существующих шаблонов
2. Настройте доступ по ссылке, как описано выше
3. Скопируйте ID документов из URL (часть между `/d/` и `/edit` в ссылке)
4. Укажите полученные ID в переменных окружения

### Устранение проблем с доступом

Если при создании проекта возникает ошибка доступа к шаблонам:

1. Убедитесь, что указанные ID в переменных окружения корректны
2. Проверьте настройки доступа к документам (должен быть включен доступ по ссылке)
3. Проверьте, что учетная запись Google, используемая для авторизации, может просматривать эти документы
4. Убедитесь, что OAuth-скоупы в приложении включают необходимые разрешения (`https://www.googleapis.com/auth/drive.file` и `https://www.googleapis.com/auth/spreadsheets`)


# TODO:
1. Calculate sheet settings 
2. Google token expiration handling
3. Align terms of reports
4. Validate that all data required for operations exists
5. Get rid of string litterals in config
6. Actualize timestamp in ProjectInfo modified field after any save