#!/bin/sh
set -e

if [ -n "$VAULT_REPO" ]; then
    if [ -d "/vault/.git" ]; then
        echo "Pulling latest vault..."
        git -C /vault pull --ff-only
    else
        echo "Cloning vault..."
        git clone --depth 1 "$VAULT_REPO" /vault
    fi
fi

exec "$@"
