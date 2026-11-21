"""Copy existing CampusAid SQLAlchemy tables into an empty PostgreSQL database.

This is a one-time, non-destructive data copy. It refuses to write into a target
that already contains rows. Set SOURCE_DATABASE_URL and TARGET_DATABASE_URL.
"""
import os
import secrets
import sys

from sqlalchemy import MetaData, Table, create_engine, func, select, text

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    source_url = os.getenv("SOURCE_DATABASE_URL", "").strip()
    target_url = os.getenv("TARGET_DATABASE_URL", "").strip()
    if not source_url or not target_url:
        raise SystemExit("Set SOURCE_DATABASE_URL and TARGET_DATABASE_URL before running this script")
    if source_url == target_url:
        raise SystemExit("Source and target database URLs must be different")

    # Reuse the project's table definitions without connecting to a default app DB.
    os.environ["APP_ENV"] = "development"
    os.environ["DATABASE_URL"] = source_url
    from app.database import Base  # noqa: E402
    from app import models  # noqa: F401,E402
    from passlib.context import CryptContext

    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    legacy_demo_names = {"student1", "worker1", "admin1", "warden1"}

    source_engine = create_engine(source_url, pool_pre_ping=True)
    target_engine = create_engine(target_url, pool_pre_ping=True)
    Base.metadata.create_all(target_engine)

    tables = list(Base.metadata.sorted_tables)
    with target_engine.connect() as target:
        existing_rows = {
            table.name: target.execute(select(func.count()).select_from(table)).scalar_one()
            for table in tables
        }
    nonempty = {name: count for name, count in existing_rows.items() if count}
    if nonempty:
        raise SystemExit(f"Refusing to import into non-empty target tables: {nonempty}")

    copied: dict[str, int] = {}
    with source_engine.connect() as source, target_engine.begin() as target:
        source_names = set(__import__("sqlalchemy").inspect(source_engine).get_table_names())
        for table in tables:
            if table.name not in source_names:
                copied[table.name] = 0
                continue
            source_table = Table(table.name, MetaData(), autoload_with=source_engine)
            source_columns = set(source_table.c.keys())
            result = source.execute(select(source_table))
            count = 0
            while batch := result.mappings().fetchmany(500):
                rows = [
                    {column.name: row[column.name] for column in table.columns if column.name in source_columns}
                    for row in batch
                ]
                if table.name == "users":
                    # Preserve rows and IDs while invalidating stock credentials
                    # created by older CampusAid versions.
                    for row in rows:
                        if row.get("username") in legacy_demo_names:
                            row["hashed_password"] = password_context.hash(secrets.token_urlsafe(48))
                target.execute(table.insert(), rows)
                count += len(batch)
            copied[table.name] = count
            if target_engine.dialect.name == "postgresql" and "id" in table.c:
                quoted = target_engine.dialect.identifier_preparer.quote(table.name)
                target.execute(
                    text(
                        f"SELECT setval(pg_get_serial_sequence(:table_name, 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {quoted}), 1), "
                        f"(SELECT MAX(id) IS NOT NULL FROM {quoted}))"
                    ),
                    {"table_name": table.name},
                )
    print(f"Copied rows by table: {copied}")
    print("Stock student1/worker1/admin1/warden1 credentials were invalidated in the destination.")
    print("Source data was not modified. Verify the destination before changing DATABASE_URL.")


if __name__ == "__main__":
    main()
