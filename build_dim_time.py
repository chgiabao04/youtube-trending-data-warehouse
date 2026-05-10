import pandas as pd

VIDEO_PATH   = "data/video_raw.csv"
COMMENT_PATH = "data/comment_raw.csv"
STATS_PATH   = "data/video_stats_raw.csv"
DIM_TIME_PATH = "warehouse/dim_time.csv"

# load data
video_df   = pd.read_csv(VIDEO_PATH)
comment_df = pd.read_csv(COMMENT_PATH)
stats_df   = pd.read_csv(STATS_PATH, low_memory=False)

# combine timestamps — thêm crawl_timestamp từ stats
times = pd.concat([
    video_df["publish_time"],
    comment_df["publish_time"],
    stats_df["crawl_timestamp"],   # ← thêm mới
])

times = pd.to_datetime(times, utc=True, errors="coerce", format="mixed")
times = times.dropna().dt.tz_convert("Asia/Ho_Chi_Minh")

dim_time = pd.DataFrame({
    "year":    times.dt.year,
    "month":   times.dt.month,
    "day":     times.dt.day,
    "hour":    times.dt.hour,
    "weekday": times.dt.weekday
})

# create time_id
dim_time["time_id"] = (
    dim_time["year"].astype(str) +
    dim_time["month"].astype(str).str.zfill(2) +
    dim_time["day"].astype(str).str.zfill(2) +
    dim_time["hour"].astype(str).str.zfill(2)
).astype(int)

# remove duplicates
dim_time = dim_time.drop_duplicates()

# reorder
dim_time = dim_time[[
    "time_id", "year", "month", "day", "hour", "weekday"
]]

# save
dim_time.to_csv(DIM_TIME_PATH, index=False)

print("DONE")
print("Total time records:", len(dim_time))