FROM python:3.12.10-bookworm

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV HOST 0.0.0.0

CMD ["fastapi", "run", "app", "--host", "0.0.0.0", "--port", "8000"]
