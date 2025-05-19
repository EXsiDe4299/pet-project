# pet-project

[RU 🇷🇺](README.md) | [EN 🇬🇧](README.en.md)

## Description

FastAPI learning project. It will improve as my skills grow.

## Installation (Linux)

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/EXsiDe4299/pet-project.git
    ```

2.  **Go to the project directory:**
    ```bash
    cd pet-project
    ```

3.  **Setting up the environment:**

    Create a `.env` file and configure the environment variables. You can see an example configuration in the `.env.template` file.

    ⚠️ **Important:** `APP_CONFIG__DB__HOST` value must be exactly the **same as the service name** in the `docker-compose.yml` file (in our case, it’s named `pg`).

    I intentionally added `private.pem` and `public.pem` to the certificates folder so that you don't have to create them. However, if you want to create your own certificates, you can do it using the following commands:

    <details>
    <summary>Creating certificates</summary>

    Go to the certificates directory
    ```bash
    cd certificates
    ```

    Generate a private key
    ```bash
    openssl genrsa -out private.pem 2048
    ```

    Extract the public key from the private key
    ```bash
    openssl rsa -in private.pem -outform PEM -pubout -out public.pem
    ```

    Go back to the project root directory
    ```bash
    cd ..
    ```

    </details>

4.  **Creating a Python virtual environment:**
    ```bash
    python3 -m venv venv
    ```
5.  **Activating the virtual environment:**
    ```bash
    source venv/bin/activate
    ```

6.  **Installing Python requirements:**
    ```bash
    pip3 install -r requirements.txt
    ```

7.  **Starting Docker Compose:**
    ```bash
    docker compose up -d
    ```

8.  **Try the app**

    Open [http://0.0.0.0:8000/docs](http://0.0.0.0:8000/docs) (you may need to replace the URL with your host and port if you use other settings in your `.env`) to view the Swagger documentation. I recommend interacting with the API using **Postman** or similar tools because for some reason Swagger can't correctly transfer jwt to my OAuth2Scheme.