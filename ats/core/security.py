import os
from datetime import timedelta

# Load from environment or fallback
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your_super_secret_key")  # 🔐 Set in .env
JWT_ALGORITHM = "HS256"
JWT_EXPIRES_IN_MINUTES = int(os.getenv("JWT_EXPIRES_IN_MINUTES", 60))  # 1 hour
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "ats_api")  # Audience for JWT