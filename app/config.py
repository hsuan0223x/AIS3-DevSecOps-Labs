import os

# Application configuration
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"

# ⚠️  教學用途：以下使用 AWS 官方文件範例 key，不是真實憑證
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
AWS_REGION = "us-east-1"

DATABASE_PATH = os.environ.get("DATABASE_PATH", "lab.db")
