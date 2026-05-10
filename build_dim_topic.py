import pandas as pd
import json

DIM_TOPIC_PATH = "warehouse/dim_topic.csv"

with open("keyword.json", "r", encoding="utf-8") as f:
    topics = json.load(f)

topic_names = list(topics.keys())

dim_topic = pd.DataFrame({
    "topic_id": range(1, len(topic_names) + 1),
    "topic_name": topic_names
})

dim_topic.to_csv(DIM_TOPIC_PATH, index=False)

print("dim_topic rebuilt")