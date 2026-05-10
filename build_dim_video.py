import pandas as pd

# =============================
# LOAD FILES
# =============================

video = pd.read_csv("data/video_raw.csv")
stats = pd.read_csv("data/video_stats_raw.csv")
dim_keyword = pd.read_csv("warehouse/dim_keyword.csv")

# =============================
# LẤY 1 SNAPSHOT MỚI NHẤT TỪ STATS
# chỉ cần metadata: category_id, duration, tags
# =============================

stats["crawl_timestamp"] = pd.to_datetime(stats["crawl_timestamp"], errors="coerce", format="mixed")

stats_latest = (
    stats.sort_values("crawl_timestamp")
    .groupby("video_id")
    .last()
    .reset_index()
)[["video_id", "category_id", "duration", "tags"]]

# =============================
# MERGE
# =============================

video["keyword"] = video["keyword"].astype(str).str.strip().str.lower()
dim_keyword["keyword"] = dim_keyword["keyword"].astype(str).str.strip().str.lower()

# Merge metadata từ stats
video = video.merge(stats_latest, on="video_id", how="left")

# Merge keyword → lấy keyword_id, topic_id
video = video.merge(dim_keyword, on="keyword", how="left")

# Chỉ giữ video có keyword_id và topic_id hợp lệ
video = video.dropna(subset=["keyword_id", "topic_id"])

# =============================
# BUILD DIM_VIDEO
# =============================

dim_video = video[[
    "video_id",
    "title",
    "channel_id",
    "thumbnail",
    "duration",
    "tags",
    "category_id",
    "keyword_id",
    "topic_id",
    "publish_time"
]]

# Mỗi video chỉ 1 dòng
dim_video = dim_video.drop_duplicates(subset="video_id")

# Fill missing
dim_video["tags"] = dim_video["tags"].fillna("")

dim_video.to_csv("warehouse/dim_video.csv", index=False)

print("dim_video created:", dim_video.shape)
print("Columns:", dim_video.columns.tolist())