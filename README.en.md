# pet-project

[RU 🇷🇺](README.md) | [EN 🇬🇧](README.en.md)

This is an educational REST API implemented using FastAPI. The project is in development. As my skills improve, I will add new endpoints, refine the code structure, and add more functionality.

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
    ```bash
    cp .env.template .env
    ```

    ⚠️ **Important:** The value of `APP_CONFIG__DB__HOST` must exactly **match the service name** in `docker-compose.yml` (in our case it is called `pg`). The same applies to `APP_CONFIG__REDIS__HOST`, its value should be identical to the one defined in `docker-compose.yml` (in our case that’s `redis`).

    I deliberately added `private.pem` and `public.pem` to the certificates directory so you don’t have to create them yourself. However, if you want to generate your own certificates, you can do so using the following commands:

    <details>
    <summary>Creating certificates</summary>
    <ol>
    <ul>

    Go to the certificates directory
    ```bash
    cd certificates
    ```
    </ul>
    
    <ul>

    Generate a private key
    ```bash
    openssl genrsa -out private.pem 2048
    ```
    </ul>

    <ul>
    
    Extract a public key from the private key
    ```bash
    openssl rsa -in private.pem -outform PEM -pubout -out public.pem
    ```
    </ul>

    <ul>
    
    Go back to the project's root directory
    ```bash
    cd ..
    ```
    </ul>
    </ol>
    </details>

4. **Run Docker Compose:**
    ```bash
    docker compose up -d
    ```

5. **Try the app:**

    Open [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) (you may need to replace the URL with your own host and port if you’re using different settings in your `.env`) to view the Swagger documentation. I recommend interacting with the API using **Postman** or similar tools, because for some reason Swagger can’t correctly pass JWTs into my OAuth2Scheme.

## Features

- **CRUD** – operations via REST API
- **Database** – PostgreSQL
- **Migrations** – Alembic
- **Authentication** – JWT (RSA certificates)
- **Blacklist** – Redis
- **Email letters** – [FastapiMail](https://github.com/sabuhish/fastapi-mail) (confirmation codes)
- **Testing** – Pytest
- **Containerization** – Docker + Docker compose

## Running tests

```bash
pytest tests
```