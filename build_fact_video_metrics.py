import pandas as pd

stats = pd.read_csv("data/video_stats_raw.csv")
dim_video = pd.read_csv("warehouse/dim_video.csv")

# chỉ giữ video hợp lệ
stats = stats[stats["video_id"].isin(dim_video["video_id"])]

# time_id từ crawl_timestamp
stats["crawl_timestamp"] = pd.to_datetime(stats["crawl_timestamp"], errors="coerce", format="mixed")
stats = stats.dropna(subset=["crawl_timestamp"])

stats["time_id"] = (
    stats["crawl_timestamp"].dt.year.astype(str) +
    stats["crawl_timestamp"].dt.month.astype(str).str.zfill(2) +
    stats["crawl_timestamp"].dt.day.astype(str).str.zfill(2) +
    stats["crawl_timestamp"].dt.hour.astype(str).str.zfill(2)
).astype(int)

fact_video_metrics = stats[[
    "video_id",
    "time_id",
    "views",
    "likes",
    "comment_count",
    "crawl_timestamp",
    "is_trending"
]]

fact_video_metrics.to_csv("warehouse/fact_video_metrics.csv", index=False)
print("fact_video_metrics created:", fact_video_metrics.shape)
