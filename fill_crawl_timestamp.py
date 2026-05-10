import pandas as pd
import numpy as np

# =============================
# LOAD FILES
# =============================

video = pd.read_csv("data/video_raw.csv")[["video_id", "crawl_time"]]

# Đọc không đặt tên cột cố định — để pandas tự detect
stats = pd.read_csv("data/video_stats_raw.csv", header=0)

print(f"Total rows: {len(stats)}")
print(f"Columns detected: {stats.columns.tolist()}")

# =============================
# ĐẢM BẢO CÓ CỘT is_trending
# =============================

if "is_trending" not in stats.columns:
    stats["is_trending"] = None
    print("Added is_trending column (was missing)")

# =============================
# TÁCH DÒNG CŨ VÀ MỚI
# =============================

old = stats[stats["crawl_timestamp"].isna()].copy()
new = stats[stats["crawl_timestamp"].notna()].copy()

print(f"\nOld rows (no timestamp): {len(old)}")
print(f"New rows (has timestamp): {len(new)}")

# =============================
# XỬ LÝ DÒNG CŨ
# =============================

old = old.merge(video, on="video_id", how="left")
old["crawl_timestamp"] = old["crawl_time"]
old = old.drop(columns=["crawl_time"])
old["is_trending"] = None

print(f"Old rows still missing timestamp: {old['crawl_timestamp'].isna().sum()}")

# =============================
# XỬ LÝ DÒNG MỚI — thiếu is_trending thì gán None
# =============================

new["is_trending"] = new["is_trending"].where(
    new["is_trending"].notna(), None
)

missing_trending = new["is_trending"].isna().sum()
print(f"New rows missing is_trending (set to None): {missing_trending}")

# =============================
# GỘP LẠI VÀ LƯU
# =============================

df_final = pd.concat([old, new], ignore_index=True)

df_final = df_final[[
    "video_id", "category_id", "duration", "tags",
    "views", "likes", "comment_count", "crawl_timestamp", "is_trending"
]]

df_final.to_csv("data/video_stats_raw.csv", index=False)

print(f"\nDONE")
print(f"Total rows saved: {len(df_final)}")
print(f"\nRows per snapshot:")
print(df_final["crawl_timestamp"].value_counts().head(5))
print(f"\nis_trending value counts:")
print(df_final["is_trending"].value_counts(dropna=False))