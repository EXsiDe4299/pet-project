# pet-project

[RU 🇷🇺](README.md) | [EN 🇬🇧](README.en.md)

Это учебный REST API, реализованный на FastAPI. Проект находится в стадии развития: по мере роста моих навыков буду
добавлять новые эндпоинты, улучшать структуру кода и расширять функциональность.

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Функционал](#функционал)
- [Запуск тестов](#запуск-тестов)

## Быстрый старт

1. **Клонируйте репозиторий:**
    ```bash
    git clone https://github.com/EXsiDe4299/pet-project.git
    ```

2. **Перейдите в директорию проекта:**
    ```bash
    cd pet-project
    ```

3. **Настройте окружение:**

    Создайте файл `.env` и настройте переменные окружения.

    - Linux:
    ```bash
    cp .env.template .env
    ```
    
    - Windows:
    ```bash
    copy .env.template .env
    ```

    Значение `APP_CONFIG__DB__HOST` должно **точно совпадать с именем сервиса** в файле `docker-compose.yml` (в нашем
    случае он называется `pg`). То же самое касается и `APP_CONFIG__REDIS__HOST`, значение этой переменной должно быть
    как в `docker-compose.yml` (в нашем случае это `redis`).
    
    Руководство по настройке SMTP-сервера можно
    посмотреть [здесь](https://yandex.ru/support/yandex-360/customers/mail/ru/mail-clients/others#smtpsetting)

    ⚠️ Я намеренно добавил `private.pem` и `public.pem` в папку certificates, чтобы вам не нужно было их создавать.
    Однако, если вы хотите создать собственные сертификаты, вы можете сделать это, используя следующие команды:

    <details>
    <summary>Создание сертификатов</summary>
    <ol>
    <ul>

    Перейдите в директорию certificates
    ```bash
    cd certificates
    ```
    </ul>

    <ul>
    
    Сгенерируйте приватный ключ
    ```bash
    openssl genrsa -out private.pem 2048
    ```
    </ul>

    <ul>
    
    Извлеките публичный ключ из приватного ключа
    ```bash
    openssl rsa -in private.pem -outform PEM -pubout -out public.pem
    ```
    </ul>
    
    <ul>
    
    Вернитесь в корневой каталог проекта
    ```bash
    cd ..
    ```
    </ul>
    </ol>
    </details>

4. **Запустите Docker Compose:**
    ```bash
    docker compose up -d
    ```

5. **Попробуйте приложение:**

    Откройте [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) (вам потребуется заменить URL-адрес вашим
    хостом и портом, если вы используете другие настройки в вашем `.env`) для просмотра документации Swagger.

## Функционал

- **CRUD** – операции через REST API
- **База данных** – PostgreSQL
- **Миграции** – Alembic
- **Аутентификация** – JWT (RSA-сертификаты)
- **Черный список** – Redis
- **Письма** – [FastapiMail](https://github.com/sabuhish/fastapi-mail) (коды подтверждения)
- **Тестирование** – Pytest
- **Контейнеризация** – Docker + Docker compose

## Запуск тестов

1. **Создайте и активируйте виртуальное окружение:**

    - Linux:
    ```bash
    python3 -m venv .venv && source .venv/bin/activate
    ```
    
    - Windows:
    ```bash
    python -m venv .venv && .venv\scripts\activate
    ```
    
2. **Установите зависимости:**
    ```bash
    pip install -r requirements.txt
    ```

3. **Запустите тесты:**
    ```bash
    pytest tests
    ```