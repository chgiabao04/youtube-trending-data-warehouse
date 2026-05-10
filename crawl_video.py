import json
import pandas as pd
import os
from dotenv import load_dotenv  
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

load_dotenv()

DATA_PATH = "data/video_raw.csv"


API_KEYS = [
    os.getenv("YOUTUBE_API_KEY_23"),
    os.getenv("YOUTUBE_API_KEY_24"),
    os.getenv("YOUTUBE_API_KEY_25"),
    os.getenv("YOUTUBE_API_KEY_26"),
    os.getenv("YOUTUBE_API_KEY_27"),
]

api_index = 0


def get_youtube():
    global api_index
    return build("youtube", "v3", developerKey=API_KEYS[api_index])


youtube = get_youtube()

# =============================
# LOAD KEYWORDS
# =============================

with open("keyword.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

videos = []
MAX_PAGES = 5

# =============================
# LOAD EXISTING VIDEOS
# =============================

existing_ids = set()

if os.path.exists(DATA_PATH):
    old_df = pd.read_csv(DATA_PATH)
    existing_ids = set(old_df["video_id"])
    print("Existing videos:", len(existing_ids))

try:

    for topic, keywords in topics.items():

        for keyword in keywords:

            print(f"\nCrawling keyword: {keyword}")

            next_page_token = None
            page = 0

            while page < MAX_PAGES:

                request = youtube.search().list(
                    q=keyword,
                    part="snippet",
                    type="video",
                    maxResults=50,
                    pageToken=next_page_token,
                    order="relevance",
                    publishedAfter="2025-01-01T00:00:00Z",
                    publishedBefore="2026-03-01T00:00:00Z"
                )

                try:

                    response = request.execute()

                except HttpError as e:

                    print("\nAPI ERROR:", e)

                    if "quotaExceeded" in str(e):

                        print("Quota exceeded. Switching API key...")

                        api_index += 1

                        if api_index >= len(API_KEYS):
                            print("All API keys exhausted.")
                            raise

                        youtube = get_youtube()
                        print("Switched to API key:", api_index + 1)

                        continue

                    else:
                        raise

                for item in response["items"]:

                    video_id = item["id"]["videoId"]

                    if video_id in existing_ids:
                        continue

                    snippet = item["snippet"]

                    videos.append({
                        "video_id": video_id,
                        "title": snippet["title"],
                        "channel_id": snippet["channelId"],
                        "channel_title": snippet["channelTitle"],
                        "publish_time": snippet["publishedAt"],
                        "description": snippet["description"],
                        "thumbnail": snippet["thumbnails"]["default"]["url"],
                        "topic": topic,
                        "keyword": keyword,
                        "crawl_time": datetime.now()
                    })

                next_page_token = response.get("nextPageToken")

                page += 1

                if not next_page_token:
                    break

finally:

    new_df = pd.DataFrame(videos)

    if os.path.exists(DATA_PATH):

        old_df = pd.read_csv(DATA_PATH)
        df = pd.concat([old_df, new_df])

    else:
        df = new_df

    df = df.drop_duplicates(subset="video_id")

    df.to_csv(DATA_PATH, index=False)

    print("\nSaved video_raw.csv")
    print("New videos:", len(new_df))
    print("Total videos:", len(df))