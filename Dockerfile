FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Optional: clone a separate vault repo at build time.
# Pass VAULT_REPO as a build arg (e.g. https://<token>@github.com/you/vault).
# If omitted, the app falls back to the bundled BlogPages/ directory.
ARG VAULT_REPO
RUN if [ -n "$VAULT_REPO" ]; then \
        apt-get update \
        && apt-get install -y --no-install-recommends git \
        && git clone --depth 1 "$VAULT_REPO" /vault \
        && rm -rf /vault/.git \
        && apt-get purge -y --auto-remove git \
        && rm -rf /var/lib/apt/lists/*; \
    fi

# VAULT_PATH=/vault is the production default.
# config.py falls back to ./BlogPages if /vault does not exist
# (i.e. when VAULT_REPO was not provided at build time).
ENV VAULT_PATH=/vault

EXPOSE 8000
CMD ["gunicorn", "-w", "5", "-b", "0.0.0.0:8000", "app:app"]
