"""Shared constants for validation and logging.

These constants centralize magic numbers and configuration values
used by the error handling and logging modules.
"""

# Validation-related constants
MIN_PASSWORD_LENGTH = 6
MAX_USERNAME_LENGTH = 150
MIN_AGE = 18
MAX_NAME_LENGTH = 200
VOTER_CARD_LENGTH = 12
MAX_PHONE_LENGTH = 20

# Logging-related constants
LOG_ROTATION_BYTES = 10 * 1024 * 1024  # 10MB
MAX_LOG_FILES = 5
REQUEST_TIMEOUT_SECONDS = 30

# Database-related constants
DEFAULT_DB_CONNECTION_TIMEOUT = 5
MAX_QUERY_TIME_SECONDS = 10
BATCH_SIZE = 100
