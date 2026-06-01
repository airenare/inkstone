import os
import sys
from urllib.parse import quote

import dotenv

dotenv.load_dotenv()

with open(os.path.join(os.path.dirname(__file__), "VERSION")) as _vf:
    VERSION = _vf.read().strip()

VAULT_PATH = os.getenv("VAULT_PATH")
if not VAULT_PATH or not os.path.exists(VAULT_PATH):
    print(
        f"WARNING: VAULT_PATH '{VAULT_PATH}' not found. "
        "Falling back to './Documentation_Website'.",
        file=sys.stderr,
    )
    VAULT_PATH = "./Documentation_Website"

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

# Optional token to unlock private notes for permitted guests.
# Set ACCESS_TOKEN in .env to any non-empty string. Visitors who
# present ?token=<value> in the URL get a session cookie and can
# browse all private notes until the session expires.
# Leave unset (default) to keep the feature disabled.
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN") or None

# Flask session signing key. Set to a long random string in production.
# If not set, sessions are invalidated on every server restart.
SECRET_KEY = os.getenv("SECRET_KEY", "inkstone-dev-secret")

# Set to "1", "true", or "yes" to remove the "built with InkStone" footer line.
HIDE_ATTRIBUTION = os.getenv("HIDE_ATTRIBUTION", "").lower() in ("1", "true", "yes")

# Giscus comment system — all three must be set to enable comments.
# Get values from https://giscus.app after linking your GitHub repo.
GISCUS_REPO = os.getenv("GISCUS_REPO") or None
GISCUS_REPO_ID = os.getenv("GISCUS_REPO_ID") or None
GISCUS_CATEGORY_ID = os.getenv("GISCUS_CATEGORY_ID") or None

# When the app is mounted below the domain root, set the same prefix the
# browser uses (e.g. "/inkstone"). All generated /attachments/ links include
# it so images work behind a path-prefix reverse proxy.
_raw_ap = (
    os.getenv("URL_PATH_PREFIX")
    or os.getenv("APPLICATION_ROOT")
    or ""
).strip().rstrip("/")
URL_PATH_PREFIX = _raw_ap


def vault_attachment_href(rel_path: str) -> str:
    """Build the public URL for a vault-relative attachment path."""
    rel = rel_path.replace("\\", "/").strip("/")
    if not rel:
        return f"{URL_PATH_PREFIX}/attachments" if URL_PATH_PREFIX else "/attachments"
    enc = "/".join(quote(seg, safe="") for seg in rel.split("/") if seg)
    base = f"{URL_PATH_PREFIX}/attachments" if URL_PATH_PREFIX else "/attachments"
    return f"{base}/{enc}"

