## Структура для чата

```
└── 📁app
    └── 📁chat
        ├── dao.py                  # Логика доступа к данным для работы с сообщениями
        ├── models.py               # Описание моделей данных (сообщения) для базы данных
        ├── router.py               # Роутеры для обработки запросов, связанных с чатом
        └── schemas.py              # Схемы Pydantic для валидации и сериализации данных чата
    └── 📁dao
        └── base.py                 # Базовый класс DAO для доступа к данным, используемый в других модулях
    └── 📁majors
    └── 📁migration
        ├── env.py
        ├── README
        └── script.py.mako
    └── 📁pages
        └── router.py
    └── 📁roles
        ├── dao.py
        ├── models.py
        ├── router.py
        ├── schemas.py
    └── 📁static                    # Статические файлы проекта (JS, CSS)
        └── 📁images
        └── 📁js
            ├── auth.js             # JavaScript логика для авторизации
            ├── chat.js             # JavaScript логика для чата
            └── script.js
        └── 📁style
            ├── auth.css            # Стили для страницы авторизации
            ├── chat.css            # Стили для страницы чата
            ├── register.css
            ├── student.css
            └── styles.css
    └── 📁students
        ├── dao.py
        ├── models.py
        ├── rb.py
        ├── router.py
        └── schemas.py
    └── 📁templates                 # HTML шаблоны для фронтенда
        ├── auth.html               # Шаблон страницы авторизации
        ├── chat.html               # Шаблон страницы чата
        ├── login_form.html
        ├── profile.html
        ├── register_form.html
        ├── student.html
        └── students.html
    └── 📁users
        ├── auth.py                 # Логика авторизации и регистрации пользователей
        ├── dao.py                  # Логика доступа к данным для работы с пользователями
        ├── dependencies.py         # Зависимости для маршрутизации (например, текущий пользователь)
        ├── models.py               # Модели данных для пользователей (SQLAlchemy)
        ├── rb.py    
        ├── router.py               # Роутеры для обработки запросов, связанных с пользователями
        └── schemas.py              # Схемы Pydantic для валидации и сериализации данных пользователей
    └── 📁utils
        └── phone_parser.py         # Утилита парсинга и модификации номера телефона под единый стандарт
    └── 📁verificationcodes         # ---- Не используется ---
        ├── dao.py
        └── models.py
    ├── config.py                   # Конфигурационный файл для настроек проекта
    ├── database.py                 # Настройки подключения к базе данных и инициализация
    ├── exceptions.py               # Обработка пользовательских исключений и ошибок
    ├── main.py                     # Основной файл запуска приложения FastAPI
    ├── majors.json
    ├── README.md
    └── students_1part.json
```