import pandas as pd
import os
from dotenv import load_dotenv  
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
youtube = build("youtube", "v3", developerKey=API_KEYS[key_index])

# =============================
# FILE PATHS
# =============================

VIDEO_PATH   = "data/video_raw.csv"      # ← sửa từ video_stats_raw
COMMENT_PATH = "data/comment_raw.csv"

# =============================
# LOAD VIDEO LIST
# =============================

video_df = pd.read_csv(VIDEO_PATH)
video_ids = video_df["video_id"].dropna().unique().tolist()  # ← thêm unique()

print(f"Total videos: {len(video_ids)}")

# =============================
# RESUME MODE
# =============================

done_videos = set()

if os.path.exists(COMMENT_PATH):
    old = pd.read_csv(COMMENT_PATH)
    done_videos = set(old["video_id"])
    print("Resume mode. Already crawled:", len(done_videos))

# =============================
# PARAMETERS
# =============================

MAX_COMMENTS = 100
BATCH_SAVE = 5000

comments = []

# =============================
# CRAWL COMMENTS
# =============================

for i, video_id in enumerate(video_ids):

    if video_id in done_videos:
        continue

    print(f"Crawling {i+1}/{len(video_ids)} : {video_id}")

    next_page_token = None
    count = 0

    while count < MAX_COMMENTS:

        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token,
                textFormat="plainText"
            )
            response = request.execute()

        except HttpError as e:
            error = str(e)
            if "quotaExceeded" in error:
                print("Quota exceeded. Switching API key...")
                key_index += 1
                if key_index >= len(API_KEYS):
                    print("No API keys left. Saving progress...")
                    break
                youtube = build("youtube", "v3", developerKey=API_KEYS[key_index])
                continue
            else:
                break

        for item in response.get("items", []):
            snippet = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "comment_id":   item.get("id"),
                "video_id":     video_id,
                "comment_text": snippet.get("textDisplay"),
                "like_count":   snippet.get("likeCount", 0),
                "publish_time": snippet.get("publishedAt"),
            })
            count += 1
            if count >= MAX_COMMENTS:
                break

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    # =============================
    # SAVE PROGRESS
    # =============================

    if len(comments) >= BATCH_SAVE:
        df = pd.DataFrame(comments)
        if os.path.exists(COMMENT_PATH):
            df.to_csv(COMMENT_PATH, mode="a", header=False, index=False)
        else:
            df.to_csv(COMMENT_PATH, index=False)
        comments = []
        print(f"  Saved batch at video {i+1}")

# =============================
# SAVE REMAINING
# =============================

if comments:
    df = pd.DataFrame(comments)
    if os.path.exists(COMMENT_PATH):
        df.to_csv(COMMENT_PATH, mode="a", header=False, index=False)
    else:
        df.to_csv(COMMENT_PATH, index=False)

print("DONE")