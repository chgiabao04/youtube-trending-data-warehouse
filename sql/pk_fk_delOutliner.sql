--Primary key-
ALTER TABLE dim_topic ADD PRIMARY KEY (topic_id);
ALTER TABLE dim_keyword ADD PRIMARY KEY (keyword_id);
ALTER TABLE dim_channel ADD PRIMARY KEY (channel_id);
ALTER TABLE dim_time ADD PRIMARY KEY (time_id);
ALTER TABLE dim_video ADD PRIMARY KEY (video_id);
ALTER TABLE fact_video_metrics ADD PRIMARY KEY (video_id, time_id); --mỗi video_id có một time_id: composite key--

--Foreign key--
ALTER TABLE dim_keyword ADD FOREIGN KEY (topic_id) REFERENCES dim_topic(topic_id);
ALTER TABLE dim_video ADD FOREIGN KEY (keyword_id) REFERENCES dim_keyword(keyword_id);
ALTER TABLE dim_video ADD FOREIGN KEY (topic_id) REFERENCES dim_topic(topic_id);
ALTER TABLE dim_video ADD FOREIGN KEY (channel_id) REFERENCES dim_channel(channel_id);
ALTER TABLE fact_video_metrics ADD FOREIGN KEY (video_id) REFERENCES dim_video(video_id);
ALTER TABLE fact_video_metrics ADD FOREIGN KEY (time_id) REFERENCES dim_time(time_id);
ALTER TABLE fact_comments ADD FOREIGN KEY (video_id) REFERENCES dim_video(video_id);
ALTER TABLE fact_comments ADD FOREIGN KEY (time_id) REFERENCES dim_time(time_id);

SELECT DISTINCT video_id
FROM fact_comments
WHERE video_id NOT IN (
    SELECT video_id FROM dim_video
);

DELETE FROM fact_comments
WHERE video_id = '36DT-tIrBIU';