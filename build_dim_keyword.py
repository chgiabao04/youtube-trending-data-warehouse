import json
import pandas as pd

DIM_TOPIC_PATH = "warehouse/dim_topic.csv"
DIM_KEYWORD_PATH = "warehouse/dim_keyword.csv"

# load topic table
dim_topic = pd.read_csv(DIM_TOPIC_PATH)

topic_map = dict(zip(dim_topic["topic_name"], dim_topic["topic_id"]))

# load keyword.json
with open("keyword.json") as f:
    data = json.load(f)

rows = []
kid = 1

for topic, keywords in data.items():

    topic_id = topic_map[topic]

    for kw in keywords:

        rows.append({
            "keyword_id": kid,
            "keyword": kw,
            "topic_id": topic_id
        })

        kid += 1

dim_keyword = pd.DataFrame(rows)

dim_keyword.to_csv(DIM_KEYWORD_PATH, index=False)

print("dim_keyword built:", len(dim_keyword))