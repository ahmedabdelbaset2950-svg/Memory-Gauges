import os
from sqlalchemy import create_engine, MetaData

# SQLite
sqlite_engine = create_engine("sqlite:///instance/mgms.db")

# PostgreSQL
postgres_engine = create_engine(os.environ["DATABASE_URL"])

sqlite_metadata = MetaData()
sqlite_metadata.reflect(bind=sqlite_engine)

postgres_metadata = MetaData()
postgres_metadata.reflect(bind=postgres_engine)

sqlite_conn = sqlite_engine.connect()
postgres_conn = postgres_engine.connect()

for table_name in sqlite_metadata.tables:

    print(f"Migrating {table_name}...")

    sqlite_table = sqlite_metadata.tables[table_name]

    rows = sqlite_conn.execute(sqlite_table.select()).fetchall()

    if not rows:
        print("  No rows.")
        continue

    postgres_table = postgres_metadata.tables.get(table_name)

    if postgres_table is None:
        print(f"  Table {table_name} not found in PostgreSQL")
        continue

    postgres_conn.execute(postgres_table.delete())

    postgres_conn.execute(
        postgres_table.insert(),
        [dict(row._mapping) for row in rows]
    )

    print(f"  Imported {len(rows)} rows.")

postgres_conn.commit()

sqlite_conn.close()
postgres_conn.close()

print("Done.")
