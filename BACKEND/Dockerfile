# API image for the local demo (compose.yaml at the repo root).
# The settings come from compose.yaml, never from a .env copied in the image.

FROM python:3.14-slim

# No .pyc files written in the image, logs shown as they come.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies first: this layer is rebuilt only when requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Not root: a flaw in the API does not give the whole container.
RUN useradd --create-home --uid 1000 api
USER api

EXPOSE 5000

CMD ["python", "-m", "app"]
