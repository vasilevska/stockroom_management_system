from datetime import timedelta
import os

redisPath = os.environ["REDIS_URL"]
#redisPath = "localhost"

class Configuration:
    # SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://root:root@{path}/"
    JWT_SECRET_KEY = "JWTSecretDevKey"
    REDIS_HOST = redisPath
    REDIS_PRODUCT_KEY = "products"
    REDIS_SUBSCRIBE_CHANNEL = "hasProducts"
    # JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    # JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
