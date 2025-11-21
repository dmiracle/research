import podcastparser
import urllib.request

FEED_URL = "https://feeds.simplecast.com/54nAGcIl"  # sample podcast feed

if __name__ == "__main__":
    with urllib.request.urlopen(FEED_URL) as resp:
        feed = podcastparser.parse(FEED_URL, resp)

    print(feed["title"])
    for episode in feed["episodes"][:3]:
        print("-", episode["title"])
