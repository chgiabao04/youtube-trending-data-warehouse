import os
import pandas as pd
from sqlalchemy import create_engine, text, inspect
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

tables = [
    ("dim_topic", "warehouse/dim_topic.csv"),      
    ("dim_channel", "warehouse/dim_channel.csv"),
    ("dim_keyword", "warehouse/dim_keyword.csv"), 
    ("dim_time", "warehouse/dim_time.csv"),
    ("dim_video", "warehouse/dim_video.csv"),
    ("fact_video_metrics", "warehouse/fact_video_metrics.csv"),
    ("fact_comments", "warehouse/fact_comments.csv"),
]

inspector = inspect(engine)
existing_tables = inspector.get_table_names()

# kiểm tra nếu bảng tồn tại thì truncate
tables_to_truncate = [t[0] for t in tables if t[0] in existing_tables]

# Thay TRUNCATE bằng DROP CASCADE
if tables_to_truncate:
    for table in tables_to_truncate:
        with engine.begin() as conn:
            conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
    print("Old tables dropped")

# load data
for table, path in tables:
    df = pd.read_csv(path)

    df.to_sql(
        table,
        engine,
        if_exists="append",
        index=False,
        method="multi",
        chunksize=10000
    )

    print(f"Loaded {table}: {len(df)} rows")