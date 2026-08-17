FROM python:3.12-slim

WORKDIR /app

# gcc is needed to build TgCrypto if no prebuilt wheel matches this platform/Python combo
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

COPY req.txt .
RUN pip install --no-cache-dir -r req.txt

COPY . .

RUN test -f bot/config.py || (echo "ERROR: bot/config.py is missing (gitignored, holds tg_id_list). Create it before building." >&2 && exit 1)

# Actual command (main_bot.py / main_userbot_linux.py) is set per-service in docker-compose.yml
CMD ["python", "main_bot.py"]
