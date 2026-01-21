# pet-project

[RU 🇷🇺](README.md) | [EN 🇬🇧](README.en.md)

This is a learning REST API implemented using FastAPI. The project is in development. As my skills improve, I will add
new endpoints, refine the code structure, and add more functionality.

## Table of Contents

- [Quick start](#quick-start)
- [Features](#features)
- [Running tests](#running-tests)

## Quick start

1. **Clone the repository:**
    ```bash
    git clone https://github.com/EXsiDe4299/pet-project.git
    ```

2. **Go to the project directory:**
    ```bash
    cd pet-project
    ```

3. **Configure the environment:**

    Create a `.env` file and configure the environment variables.
    
    - Linux:
    ```bash
    cp .env.template .env
    ```

    - Windows:
    ```bash
    copy .env.template .env
    ```

    The value of `APP_CONFIG__DB__HOST` must exactly **match the service name** in `docker-compose.yml` (in our case it
    is called `pg`). The same applies to `APP_CONFIG__REDIS__HOST`, its value should be identical to the one defined in
    `docker-compose.yml` (in our case that’s `redis`). Also, if you want to change the port value, you should change it 
    in the `nginx.conf` file as well.

    You can check the SMTP server configuration guide [here](https://yandex.com/support/yandex-360/customers/mail/en/mail-clients/others#smtpsetting)

4. **Run Docker Compose:**
    ```bash
    docker compose up -d
    ```

5. **Try the app:**

    Open https://localhost/docs to view the Swagger documentation. You might see a message stating that a secure 
    connection cannot be established. This is normal because the project uses self-signed SSL certificates. Just click
    on the "More details" button, and then on "Continue to site".

## Features

- **CRUD** – operations via REST API
- **Database** – PostgreSQL
- **Migrations** – Alembic
- **Authentication** – JWT (RSA certificates)
- **Blacklist** – Redis
- **Email letters** – [FastapiMail](https://github.com/sabuhish/fastapi-mail) (confirmation codes)
- **Testing** – Pytest
- **Containerization** – Docker + Docker compose
- **Reverse proxy** – Nginx

## Running tests

1. **Create and activate virtual environment:**
    
    - Linux:
    ```bash
    uv venv && source .venv/bin/activate
    ```
   
    - Windows:
    ```bash
    uv venv && .venv\scripts\activate
    ```

2. **Install requirements:**
    ```bash
    uv sync
    ```

3. **Run the tests:**
    ```bash
    uv run pytest
    ```