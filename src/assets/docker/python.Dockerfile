# ────────────── First stage ──────────────
FROM python:3.13-slim AS build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN python -m venv .venv

ENV PATH="/app/.venv/bin:$PATH"

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# ────────────── Second stage ──────────────
FROM python:3.13-slim

RUN useradd --create-home appUser
USER appUser

WORKDIR /app

COPY src ./src
COPY --from=build /app/.venv .venv

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
