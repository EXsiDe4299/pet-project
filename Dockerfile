FROM python:3.12.3-bookworm

ENV PYTHONBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x prestart.sh

ENTRYPOINT ["./prestart.sh"]
CMD ["python3", "main.py"]
