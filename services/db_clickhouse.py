import os
import csv
import io
from datetime import datetime
import logging

import clickhouse_connect

logger = logging.getLogger(__name__)


def get_client():
    host = os.getenv("CLICKHOUSE_HOST", "clickhouse-server")
    port = int(os.getenv("CLICKHOUSE_PORT", "8123"))
    username = os.getenv("CLICKHOUSE_USER", "default")
    password = os.getenv("CLICKHOUSE_PASSWORD", "")
    database = os.getenv("CLICKHOUSE_DB", "default")
    client = clickhouse_connect.get_client(
        host=host, port=port, username=username, password=password, database=database
    )
    return client


def ensure_table():
    client = get_client()
    create_sql = """
    CREATE TABLE IF NOT EXISTS suppliers (
        category String,
        keyword String,
        company String,
        profile_link String,
        price_basis String,
        price String,
        currency String,
        certificates String,
        status String,
        notes String,
        score Int32,
        scraped_at DateTime
    ) ENGINE = MergeTree()
    ORDER BY (profile_link, scraped_at)
    """
    client.command(create_sql)
    logger.info("Ensured ClickHouse table 'suppliers' exists")


def insert_suppliers(rows: list[list[str]]):
    """
    Insert rows into ClickHouse. Rows expected in the same order as columns below.
    Columns: category, keyword, company, profile_link, price_basis, price, currency, certificates, status, notes, score, scraped_at
    """
    if not rows:
        return 0
    ensure_table()
    client = get_client()

    # Prepare tuples and filter duplicates already present
    profile_links = [r[3] for r in rows if r[3]]
    existing = set()
    if profile_links:
        q = (
            "SELECT profile_link FROM suppliers WHERE profile_link IN (%s)"
            % ",".join("'%s'" % link.replace("'", "\\'") for link in set(profile_links))
        )
        try:
            resp = client.query(q)
            for rec in resp.result_rows:
                existing.add(rec[0])
        except Exception:
            # If query fails (very long IN list) fall back to no pre-check and rely on MergeTree
            existing = set()

    insert_rows = []
    for r in rows:
        if r[3] and r[3] in existing:
            continue
        # ensure score
        try:
            score = int(r[9].split(']')[0].split(':')[-1].strip().split('/')[0]) if r[9] else 0
        except Exception:
            score = 0
        scraped_at = datetime.utcnow()
        insert_rows.append(
            {
                "category": r[0],
                "keyword": r[1],
                "company": r[2],
                "profile_link": r[3],
                "price_basis": r[4],
                "price": r[5],
                "currency": r[6],
                "certificates": r[7],
                "status": r[8],
                "notes": r[9],
                "score": score,
                "scraped_at": scraped_at,
            }
        )

    if not insert_rows:
        logger.info("No new rows to insert into ClickHouse")
        return 0

    # Bulk insert
    columns = [
        "category",
        "keyword",
        "company",
        "profile_link",
        "price_basis",
        "price",
        "currency",
        "certificates",
        "status",
        "notes",
        "score",
        "scraped_at",
    ]
    # Convert dicts to tuples in column order
    data_tuples = [tuple(item[col] for col in columns) for item in insert_rows]
    client.insert(table="suppliers", data=data_tuples, column_names=columns)
    logger.info("Inserted %d new rows into ClickHouse", len(data_tuples))
    return len(data_tuples)


def fetch_suppliers_csv(limit: int | None = None) -> bytes:
    ensure_table()
    client = get_client()
    q = "SELECT category, keyword, company, profile_link, price_basis, price, currency, certificates, status, notes, score, scraped_at FROM suppliers ORDER BY scraped_at DESC"
    if limit:
        q += f" LIMIT {limit}"
    result = client.query(q)
    rows = result.result_rows

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "category",
        "keyword",
        "company",
        "profile_link",
        "price_basis",
        "price",
        "currency",
        "certificates",
        "status",
        "notes",
        "score",
        "scraped_at",
    ])
    for r in rows:
        writer.writerow(r)

    return output.getvalue().encode("utf-8")
