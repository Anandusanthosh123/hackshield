import os
import json
import requests
import feedparser

CACHE_NEWS = "news_cache.json"
CACHE_JOBS = "jobs_cache.json"

CYBER_NEWS_FEEDS = [
    "https://www.bleepingcomputer.com/feed/",
    "https://www.securityweek.com/feed",
    "https://feeds.feedburner.com/TheHackersNews"
]

CYBER_JOBS_FEED = [
    "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=cybersecurity",
]


def fetch_news():
    news_list = []

    try:
        for feed_url in CYBER_NEWS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:
                news_list.append({
                    "title": entry.title,
                    "link": entry.link,
                })

        # Save to cache
        with open(CACHE_NEWS, "w") as f:
            json.dump(news_list, f)

        return news_list

    except:
        # Offline fallback
        if os.path.exists(CACHE_NEWS):
            with open(CACHE_NEWS, "r") as f:
                return json.load(f)

        return []
    


def fetch_jobs():
    job_list = []

    try:
        # LinkedIn unofficial feed
        response = requests.get(CYBER_JOBS_FEED[0], timeout=5)
        if response.status_code == 200:
            data = response.text.split('<a')  # Simple offline-compatible parsing
            for block in data[:10]:
                if "job-title" in block:
                    title = block.split(">")[1].split("<")[0]
                    job_list.append({"title": title})

        with open(CACHE_JOBS, "w") as f:
            json.dump(job_list, f)

        return job_list

    except:
        if os.path.exists(CACHE_JOBS):
            with open(CACHE_JOBS, "r") as f:
                return json.load(f)

        return []
