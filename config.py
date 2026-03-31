import os

import dotenv

dotenv.load_dotenv()

VAULT_PATH = os.getenv("VAULT_PATH")
if not VAULT_PATH or not os.path.exists(VAULT_PATH):
    print(
        f"Warning: VAULT_PATH '{VAULT_PATH}' does not exist. "
        "Using './BlogPages' for testing."
    )
    VAULT_PATH = "./BlogPages"

BLOG_TAGS = {"blog", "website"}
HOMEPAGE_TAG = "homepage"
FEATURED_TAG = "featured"
LISTING_TAG = "listing"
