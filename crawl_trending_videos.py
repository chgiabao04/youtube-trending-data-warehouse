from dotenv import load_dotenv
import pandas as pd
import os
from dotenv import load_dotenv  
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# =============================
# API KEYS
# =============================

load_dotenv()

API_KEYS = [
    os.getenv("YOUTUBE_API_KEY_1"),
    os.getenv("YOUTUBE_API_KEY_2"),
    os.getenv("YOUTUBE_API_KEY_3"),
    os.getenv("YOUTUBE_API_KEY_4"),
    os.getenv("YOUTUBE_API_KEY_5"),
    os.getenv("YOUTUBE_API_KEY_6")
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
# MAP category_id → topic + keyword
# =============================

CATEGORY_MAP = {
    "10": ("music",         "official music video"),
    "17": ("fitness",       "fitness routine"),
    "19": ("travel",        "travel vlog"),
    "20": ("gaming",        "gaming highlights"),
    "22": ("vlog",          "daily vlog"),
    "23": ("vlog",          "daily vlog"),
    "24": ("entertainment", "funny videos compilation"),
    "25": ("food",          "food review"),
    "26": ("education",     "programming tutorial"),
    "27": ("education",     "programming tutorial"),
    "28": ("technology",    "tech review"),
    "29": ("vlog",          "daily vlog"),
    "43": ("vlog",          "daily vlog"),
}

DEFAULT_TOPIC   = "entertainment"
DEFAULT_KEYWORD = "funny videos compilation"

# =============================
# LOAD EXISTING VIDEO IDS
# =============================

existing_ids = set()

if os.path.exists(VIDEO_PATH):
    old_df = pd.read_csv(VIDEO_PATH)
    existing_ids = set(old_df["video_id"])
    print(f"Existing videos: {len(existing_ids)}")

# =============================
# LOAD ALL COUNTRIES FROM DATA
# =============================

channel_df = pd.read_csv(CHANNEL_PATH)
all_regions = channel_df["country"].dropna().unique().tolist()
print(f"Crawling trending for {len(all_regions)} countries...")

# =============================
# CRAWL TRENDING VIDEOS
# =============================

crawl_time = datetime.now()
videos = []

for region in all_regions:
    try:
        request = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            chart="mostPopular",
            regionCode=region,
            maxResults=50
        )
        response = request.execute()

        count = 0
        for item in response.get("items", []):

            video_id = item.get("id")

            if video_id in existing_ids:
                continue

            snippet    = item.get("snippet", {})
            statistics = item.get("statistics", {})
            content    = item.get("contentDetails", {})

            category_id = str(snippet.get("categoryId", ""))
            topic, keyword = CATEGORY_MAP.get(category_id, (DEFAULT_TOPIC, DEFAULT_KEYWORD))

            videos.append({
                "video_id":      video_id,
                "title":         snippet.get("title"),
                "channel_id":    snippet.get("channelId"),
                "channel_title": snippet.get("channelTitle"),
                "publish_time":  snippet.get("publishedAt"),
                "description":   snippet.get("description", ""),
                "thumbnail":     snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "topic":         topic,
                "keyword":       keyword,
                "crawl_time":    crawl_time,
            })

            existing_ids.add(video_id)
            count += 1

        print(f"  {region}: {count} new trending videos")

    except HttpError as e:
        error = str(e)
        if "quotaExceeded" in error:
            print(f"  {region}: Quota exceeded. Switching API key...")
            key_index += 1
            if key_index >= len(API_KEYS):
                print("All API keys exhausted.")
                break
            youtube = get_youtube()
        else:
            print(f"  {region}: Error - {e}")
        continue

# =============================
# SAVE — APPEND vào video_raw.csv
# =============================

new_df = pd.DataFrame(videos)

print(f"\nNew trending videos collected: {len(new_df)}")

if len(new_df) == 0:
    print("No new trending videos found.")
else:
    if os.path.exists(VIDEO_PATH):
        old_df = pd.read_csv(VIDEO_PATH)
        df = pd.concat([old_df, new_df], ignore_index=True)
    else:
        df = new_df

    df = df.drop_duplicates(subset="video_id")
    df.to_csv(VIDEO_PATH, index=False)

    print(f"Total videos in video_raw.csv: {len(df)}")

print("\nDONE")
print(f"Crawl time: {crawl_time}")