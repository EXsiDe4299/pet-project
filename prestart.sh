#!/usr/bin/env bash

set -e

echo "Generate JWT keys..."
openssl genrsa -out certificates/private.pem 2048
openssl rsa -in certificates/private.pem -outform PEM -pubout -out certificates/public.pem

chmod o+r certificates/private.pem
chmod o+r certificates/public.pem
echo "Keys generated"


echo "Generate ssl certificates..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certificates/ssl_certificate_key.pem -out certificates/ssl_certificate.pem -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

chmod o+r certificates/ssl_certificate.pem
chmod o+r certificates/ssl_certificate_key.pem
echo "Certificates generated"


echo "Apply migrations..."
uv run alembic upgrade head
echo "Migrations applied"

exec "$@"