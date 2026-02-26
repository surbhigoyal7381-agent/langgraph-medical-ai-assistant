import os
from typing import List


def _split_origins(val: str) -> List[str]:
    return [s.strip() for s in val.split(',') if s.strip()]


class Settings:
    """Runtime settings for the backend.

    - Read `ALLOWED_ORIGINS` as a comma-separated list for CORS in production.
    - If `ENV` is `production` and `ALLOWED_ORIGINS` is empty, raise a ValueError
      to avoid accidentally allowing all origins in prod.
    """

    ENV: str = os.environ.get('ENV', 'development')
    # Comma separated list; e.g. "https://app.example.com,https://admin.example.com"
    ALLOWED_ORIGINS: List[str] = _split_origins(os.environ.get('ALLOWED_ORIGINS', ''))

    @classmethod
    def require_production_safe(cls):
        if cls.ENV == 'production' and not cls.ALLOWED_ORIGINS:
            raise ValueError('ALLOWED_ORIGINS must be set in production and must not be empty')


# Module-level settings instance
settings = Settings()
