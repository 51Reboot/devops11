import os


class Config(object):
    """Base config class."""
    DEBUG = True

    # MYSQL Default
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "12345678"
    MYSQL_DB = "ops11"
    MYSQL_CHARSET = "utf8mb4"
    MYSQL_UNIX_SOCKET = ""

    # REDIS Default
    REDIS_HOST = "127.0.0.1"
    REDIS_PASSWORD = ""
    REDIS_PORT = 6379


class DevelopmentConfig(Config):
    """Development config class."""
    DEBUG = True
    MYSQL_DB = "ops1"


class ProductionConfig(Config):
    """Production config class."""
    DEBUG = False

    # MYSQL Default
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "123456"
    MYSQL_DB = "ops"
    MYSQL_CHARSET = "utf8mb4"
    MYSQL_UNIX_SOCKET = ""

    # REDIS Default
    REDIS_HOST = "127.0.0.1"
    REDIS_PASSWORD = ""
    REDIS_PORT = 6379


if os.environ.get("OPS11_APP_ENV") == "release":
    Config = ProductionConfig()
else:
    Config = DevelopmentConfig()