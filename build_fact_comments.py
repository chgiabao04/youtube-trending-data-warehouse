import pandas as pd

COMMENT_PATH = "data/comment_raw.csv"
FACT_PATH = "warehouse/fact_comments.csv"
DIM_VIDEO_PATH = "warehouse/dim_video.csv"

comments = pd.read_csv(COMMENT_PATH)
dim_video = pd.read_csv(DIM_VIDEO_PATH)

# chỉ giữ comment của video hợp lệ
comments = comments[
    comments["video_id"].isin(dim_video["video_id"])
]

# convert datetime (UTC → VN)
comments["publish_time"] = pd.to_datetime(
    comments["publish_time"],
    utc=True,
    errors="coerce"
)

comments = comments.dropna(subset=["publish_time"])

comments["publish_time"] = comments["publish_time"].dt.tz_convert("Asia/Ho_Chi_Minh")

# create time_id
comments["time_id"] = (
    comments["publish_time"].dt.year.astype(str) +
    comments["publish_time"].dt.month.astype(str).str.zfill(2) +
    comments["publish_time"].dt.day.astype(str).str.zfill(2) +
    comments["publish_time"].dt.hour.astype(str).str.zfill(2)
).astype(int)

fact_comments = comments[
[
"comment_id",
"video_id",
"time_id",
"comment_text",
"like_count"
]
]

# remove duplicate comments
fact_comments = fact_comments.drop_duplicates(subset="comment_id")

fact_comments.to_csv(FACT_PATH, index=False)

print("fact_comments created:", fact_comments.shape)