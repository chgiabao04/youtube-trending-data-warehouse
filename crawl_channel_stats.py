import pandas as pd
import os
from dotenv import load_dotenv  
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()

API_KEYS = [
    os.getenv("YOUTUBE_API_KEY_1"),
    os.getenv("YOUTUBE_API_KEY_2"),
    os.getenv("YOUTUBE_API_KEY_3")
]

key_index = 0


def get_youtube():
    global key_index
    return build("youtube", "v3", developerKey=API_KEYS[key_index])


youtube = get_youtube()

# =============================
# PATHS
# =============================

VIDEO_PATH   = "data/video_raw.csv"
CHANNEL_PATH = "data/channel_stats_raw.csv"

# =============================
# LOAD CHANNEL IDS — CHỈ LẤY MỚI
# =============================

video_df = pd.read_csv(VIDEO_PATH)
all_channel_ids = video_df["channel_id"].dropna().unique().tolist()

# Chỉ crawl channel chưa có trong file cũ
existing_ids = set()

if os.path.exists(CHANNEL_PATH):
    existing = pd.read_csv(CHANNEL_PATH)
    existing_ids = set(existing["channel_id"])
    print(f"Existing channels: {len(existing_ids)}")

channel_ids = [c for c in all_channel_ids if c not in existing_ids]
print(f"New channels to crawl: {len(channel_ids)}")

if len(channel_ids) == 0:
    print("No new channels to crawl.")
    exit()

# =============================
# CRAWL
# =============================

channels = []
BATCH_SIZE = 50

for i in range(0, len(channel_ids), BATCH_SIZE):

    batch = channel_ids[i:i + BATCH_SIZE]
    print(f"Crawling channels {i} -> {i + len(batch)}")

    while True:
        try:
            request = youtube.channels().list(
                part="snippet,statistics",
                id=",".join(batch)
            )
            response = request.execute()
            break

        except HttpError as e:
            error = str(e)
            if "quotaExceeded" in error:
                print("Quota exceeded. Switching API key...")
                key_index += 1
                if key_index >= len(API_KEYS):
                    print("All API keys exhausted.")
                    break
                youtube = get_youtube()
                continue
            else:
                print(f"API error: {e}")
                break

    for item in response.get("items", []):

        snippet = item.get("snippet", {})
        stats   = item.get("statistics", {})

        channels.append({
            "channel_id":       item.get("id"),
            "channel_title":    snippet.get("title"),
            "country":          snippet.get("country"),
            "subscriber_count": int(stats.get("subscriberCount", 0)),
            "video_count":      int(stats.get("videoCount", 0)),
            "total_views":      int(stats.get("viewCount", 0)),
        })

# =============================
# SAVE — APPEND
# =============================

new_df = pd.DataFrame(channels)
print(f"\nNew channels collected: {len(new_df)}")

if len(new_df) > 0:
    if os.path.exists(CHANNEL_PATH):
        old = pd.read_csv(CHANNEL_PATH)
        df = pd.concat([old, new_df], ignore_index=True)
    else:
        df = new_df

    df = df.drop_duplicates(subset="channel_id")
    df["country"] = df["country"].fillna("Unknown")
    df.to_csv(CHANNEL_PATH, index=False)
    print(f"Total channels saved: {len(df)}")

print("\nDONE")