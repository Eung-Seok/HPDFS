import os


API_URL = os.getenv("HPDFS_API_URL", "http://localhost").rstrip("/")

# 수집 간격 (분)
INTERVAL_MINUTES = int(os.getenv("HPDFS_INTERVAL_MINUTES", "5"))

# 요청 타임아웃 (초)
REQUEST_TIMEOUT = int(os.getenv("HPDFS_REQUEST_TIMEOUT", "10"))
