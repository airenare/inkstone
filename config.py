import os
import sys

import dotenv

dotenv.load_dotenv()

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as _vf:
    VERSION = _vf.read().strip()

VAULT_PATH = os.getenv("VAULT_PATH")
if not VAULT_PATH or not os.path.exists(VAULT_PATH):
    print(
        f"WARNING: VAULT_PATH '{VAULT_PATH}' not found. "
        "Falling back to './BlogPages' (demo vault).",
        file=sys.stderr,
    )
    VAULT_PATH = "./BlogPages"

# Optional vault-wide attachments directory.
# Set ATTACHMENTS_PATH in .env to a directory that is checked as a fallback
# when a media file is not found in the note's own _attachments/ folder.
# If unset, the engine also auto-checks _attachments/ at the vault root.
ATTACHMENTS_PATH = os.getenv("ATTACHMENTS_PATH") or None
if ATTACHMENTS_PATH and not os.path.isdir(ATTACHMENTS_PATH):
    print(
        f"WARNING: ATTACHMENTS_PATH '{ATTACHMENTS_PATH}' is not a directory. Ignoring.",
        file=sys.stderr,
    )
    ATTACHMENTS_PATH = None

VAULT_REPO = os.getenv("VAULT_REPO") or None
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET") or None

