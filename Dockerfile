FROM python:3.12.3-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONBUFFERED=1

ENV UV_NO_DEV=1

WORKDIR /app

COPY pyproject.toml ./pyproject.toml

RUN uv sync

COPY . /app

RUN chmod +x prestart.sh

ENTRYPOINT ["./prestart.sh"]
CMD ["uv", "run", "main.py"]
