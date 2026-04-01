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

BLOG_TAGS = {"blog", "website"}
HOMEPAGE_TAG = "homepage"
FEATURED_TAG = "featured"
LISTING_TAG = "listing"
