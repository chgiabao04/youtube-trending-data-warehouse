# YouTube Trending Data Warehouse & Analytics -- In Progress

This project builds an end-to-end YouTube Trending analytics pipeline using YouTube API, data warehouse modeling, and exploratory data analysis to analyze trending video behavior across multiple countries.

---

## 🔍 Project Overview

This project builds an end-to-end data pipeline for YouTube trending data:

- **Crawl** trending videos, channel stats, comments, and video statistics via YouTube Data API v3
- **Model** the data into a star schema Data Warehouse (PostgreSQL)
- **Analyze** trending patterns across regions, categories, and time
- **Predict** *(In Progress)* whether a video will trend using ML models

---

## 📦 Dataset

| Table | Records | Description |
|---|---|---|
| Trending Videos | ~100,000+ | Crawled across 3 sessions, 109 countries |
| Comments | ~1,000,000+ | Comments from trending videos |
| Channel Stats | — | Subscriber count, view count, country |
| Video Statistics | — | Views, likes, comment count per video |

> Data is not included in this repo due to size. Raw CSVs stored locally.

---

## 🗂️ Data Warehouse Schema (Star Schema)

```
fact_video_metrics
    ├── dim_video       (video_id, title, description, thumbnail, publish_time)
    ├── dim_channel     (channel_id, channel_title, country, subscriber_count)
    ├── dim_time        (date, day, month, year, weekday)
    ├── dim_topic       (topic_id, topic_name)
    └── dim_keyword     (keyword_id, keyword)

fact_comments
    └── dim_video
```

---

## ⚙️ Pipeline

```
YouTube Data API v3
        │
        ▼
  Crawl Scripts (Python)
  ├── crawl_trending_videos.py   → trending videos by country
  ├── crawl_video_statistics.py  → views, likes, comments
  ├── crawl_channel_stats.py     → channel metadata
  └── crawl_comments.py          → top comments per video
        │
        ▼
  Raw CSVs (local)
        │
        ▼
  Processing & Cleaning (processing.ipynb)
        │
        ▼
  Build Dimensions & Facts (Python)
  ├── build_dim_video.py
  ├── build_dim_channel.py
  ├── build_dim_time.py
  ├── build_dim_topic.py
  ├── build_dim_keyword.py
  ├── build_fact_video_metrics.py
  └── build_fact_comments.py
        │
        ▼
  load_dw.py → PostgreSQL
        │
        ▼
  EDA (EDA/)
        │
        ▼
  ML Trending Prediction (In Progress)
```

---

## 🛠️ Tech Stack

| Layer | Tools |
|---|---|
| Data Collection | Python, YouTube Data API v3 |
| Data Processing | Pandas, NumPy |
| Data Warehouse | PostgreSQL |
| EDA | Jupyter Notebook, Matplotlib, Seaborn |
| ML *(planned)* | Scikit-learn, XGBoost |

---

## 🌍 Countries Crawled

Trending videos collected from all countries available via channel stats data, covering major regions across Asia, Europe, and the Americas.

---

## 🔑 API Key Rotation

To handle YouTube Data API quota limits (10,000 units/day per key), the pipeline supports **automatic rotation across 6 API keys** — switching keys when quota is exceeded without interrupting the crawl.

---

## 📁 Project Structure

```
├── crawl_trending_videos.py      # Crawl trending videos by country
├── crawl_video_statistics.py     # Crawl views, likes, comment count
├── crawl_channel_stats.py        # Crawl channel metadata
├── crawl_comments.py             # Crawl top comments
├── fill_crawl_timestamp.py       # Fill missing crawl timestamps
├── build_dim_*.py                # Build dimension tables
├── build_fact_*.py               # Build fact tables
├── load_dw.py                    # Load all tables into PostgreSQL
├── connect.py                    # DB connection config
├── processing.ipynb              # Data cleaning & processing
├── keyword.json                  # Category → keyword mapping
├── EDA/                          # Exploratory Data Analysis
└── sql/                          # SQL scripts
```

---

## 🚧 In Progress

- [ ] Re-run EDA on latest crawled data (~100K videos, ~1M comments)
- [ ] Feature engineering for ML model
- [ ] Build ML model to predict video trending probability
- [ ] Power BI / dashboard for trend visualization

---

## 🚀 Setup

1. Clone the repo
2. Create `.env` file with your YouTube API keys:
```
YOUTUBE_API_KEY_1=your_key_here
YOUTUBE_API_KEY_2=your_key_here
...
```
3. Configure PostgreSQL connection in `connect.py`
4. Run crawl scripts → `processing.ipynb` → `load_dw.py`