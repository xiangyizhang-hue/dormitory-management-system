import os


def mysql_config(*, include_database: bool = True) -> dict:
    """Build connection settings from environment variables; no password is stored in source."""
    config = {
        "host": os.getenv("DORM_DB_HOST", "127.0.0.1"),
        "user": os.getenv("DORM_DB_USER", "root"),
        "password": os.getenv("DORM_DB_PASSWORD", ""),
        "port": int(os.getenv("DORM_DB_PORT", "3306")),
        "charset": "utf8mb4",
        "autocommit": False,
    }
    if include_database:
        config["database"] = os.getenv("DORM_DB_NAME", "dorm_manage_system")
    return config
