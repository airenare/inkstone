FROM python:3.11-slim

# git is needed at runtime to clone/pull the vault
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt
RUN chmod +x /app/entrypoint.sh

# VAULT_PATH=/vault is the production default.
# config.py falls back to ./Documentation_Website if /vault does not exist.
ENV VAULT_PATH=/vault

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "-w", "5", "-b", "0.0.0.0:8000", "app:app"]
