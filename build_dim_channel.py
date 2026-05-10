import pandas as pd

CHANNEL_PATH = "data/channel_stats_raw.csv"
DIM_CHANNEL_PATH = "warehouse/dim_channel.csv"

df = pd.read_csv(CHANNEL_PATH)

dim_channel = df[[
    "channel_id",
    "channel_title",
    "country",
    "subscriber_count",
    "video_count",
    "total_views"
]]

# remove duplicate channel
dim_channel = dim_channel.drop_duplicates(subset="channel_id")

# fix missing country
dim_channel["country"] = dim_channel["country"].fillna("Unknown")

# convert numeric
dim_channel["subscriber_count"] = pd.to_numeric(dim_channel["subscriber_count"], errors="coerce")
dim_channel["video_count"] = pd.to_numeric(dim_channel["video_count"], errors="coerce")
dim_channel["total_views"] = pd.to_numeric(dim_channel["total_views"], errors="coerce")

dim_channel.to_csv(DIM_CHANNEL_PATH, index=False)

print("dim_channel built:", len(dim_channel))