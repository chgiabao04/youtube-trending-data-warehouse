import pandas as pd
import os
from dotenv import load_dotenv  
from datetime import datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

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
STATS_PATH   = "data/video_stats_raw.csv"

# =============================
# CRAWL TIMESTAMP
# =============================

crawl_timestamp = datetime.now().isoformat()
print(f"Crawl timestamp: {crawl_timestamp}")

# =============================
# STEP 1: CRAWL TRENDING LIST
# lấy tất cả countries có trong data
# =============================

channel_df = pd.read_csv(CHANNEL_PATH)
all_regions = channel_df["country"].dropna().unique().tolist()
print(f"\nCrawling trending for {len(all_regions)} countries...")

trending_ids = set()

for region in all_regions:
    try:
        request = youtube.videos().list(
            part="id",
            chart="mostPopular",
            regionCode=region,
            maxResults=50
        )
        response = request.execute()
        count = len(response.get("items", []))
        for item in response.get("items", []):
            trending_ids.add(item["id"])
        print(f"  {region}: {count} trending videos")

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

print(f"Total unique trending videos: {len(trending_ids)}")

# =============================
# STEP 2: LOAD VIDEO LIST
# =============================

df = pd.read_csv(VIDEO_PATH)
video_ids = df["video_id"].dropna().unique().tolist()
print(f"\nTotal videos to crawl: {len(video_ids)}")

# =============================
# STEP 3: CRAWL VIDEO STATS
# =============================

stats = []
BATCH_SIZE = 50

for i in range(0, len(video_ids), BATCH_SIZE):

    batch_ids = video_ids[i:i + BATCH_SIZE]
    print(f"Crawling videos {i} -> {i + len(batch_ids)}")

    response = None

    while True:
        try:
            request = youtube.videos().list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch_ids)
            )
            response = request.execute()
            break

        except HttpError as e:
            error = str(e)
            if "quotaExceeded" in error:
                print("Quota exceeded. Switching API key...")
                key_index += 1
                if key_index >= len(API_KEYS):
                    print("All API keys exhausted. Saving progress...")
                    response = {"items": []}
                    break
                youtube = get_youtube()
                continue
            else:
                print(f"API error: {e}")
                response = {"items": []}
                break

    if response is None:
        print(f"Batch {i} failed - skipping")
        continue

    for item in response.get("items", []):

        video_id = item.get("id")
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        content = item.get("contentDetails", {})

        stats.append({
            "video_id":        video_id,
            "category_id":     snippet.get("categoryId"),
            "duration":        content.get("duration"),
            "tags":            ",".join(snippet.get("tags", [])),
            "views":           int(statistics.get("viewCount", 0)),
            "likes":           int(statistics.get("likeCount", 0)),
            "comment_count":   int(statistics.get("commentCount", 0)),
            "crawl_timestamp": crawl_timestamp,
            "is_trending":     video_id in trending_ids,  # ← True/False
        })

# =============================
# STEP 4: SAVE — APPEND MODE
# =============================

if len(stats) == 0:
    print("No data collected")
else:
    stats_df = pd.DataFrame(stats)

    if os.path.exists(STATS_PATH):
        stats_df.to_csv(STATS_PATH, mode="a", header=False, index=False)
        print(f"\nAppended {len(stats_df)} records to {STATS_PATH}")
    else:
        stats_df.to_csv(STATS_PATH, index=False)
        print(f"\nCreated {STATS_PATH} with {len(stats_df)} records")

print("\nDONE")
print(f"Crawl timestamp: {crawl_timestamp}")
print(f"Trending videos found: {len(trending_ids)}")