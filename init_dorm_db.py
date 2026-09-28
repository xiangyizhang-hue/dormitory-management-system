from pathlib import Path

import pymysql

from db_config import mysql_config


def iter_sql_statements(sql_text: str):
    cleaned_lines = []
    for line in sql_text.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            cleaned_lines.append(line)
    for statement in "\n".join(cleaned_lines).split(";"):
        if statement.strip():
            yield statement.strip()


def main():
    schema_path = Path(__file__).with_name("schema.sql")
    connection = pymysql.connect(**mysql_config(include_database=False))
    try:
        with connection.cursor() as cursor:
            for statement in iter_sql_statements(schema_path.read_text(encoding="utf-8")):
                cursor.execute(statement)
        connection.commit()
        print("数据库和数据表初始化成功。")
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


if __name__ == "__main__":
    main()
