import feedparser

FEED_URL = "https://planetpython.org/rss20.xml"

if __name__ == "__main__":
    feed = feedparser.parse(FEED_URL)
    print(feed.feed.title)
    for entry in feed.entries[:3]:
        print("-", entry.title)
